import asyncio
import json
import os

import pytest

from anylumino.workbench import Workbench, skill
from anylumino.workbench.agents import AgentRunner
from anylumino.workbench.prompt import system_prompt
from anylumino.workbench.skill import Skill, read_skill
from test_workbench import reply


def skill_folder(root, name="trading-chart", front_matter=None):
    folder = root / name
    folder.mkdir(parents=True)
    fields = front_matter if front_matter is not None else f"name: {name}\ndescription: Draws candles with NotebookChart."
    (folder / "SKILL.md").write_text(f"---\n{fields}\n---\n\n# Charts\n")
    (folder / "reference.md").write_text("API reference\n")

    return folder


def test_read_skill_returns_the_front_matter_and_resolved_path(tmp_path):
    folder = skill_folder(tmp_path, front_matter='name: trading-chart\ndescription: "Draws candles: one pane per series."')

    assert read_skill(folder) == Skill("trading-chart", "Draws candles: one pane per series.", folder.resolve())


@pytest.mark.parametrize(
    ("front_matter", "message"),
    [
        (None, "is not a skill folder: it has no SKILL.md"),
        ("name: trading-chart", "needs front matter with a name and a description"),
        ("name: Trading Chart\ndescription: Charts.", "the skill name 'Trading Chart' must use lowercase letters, digits, and '-'"),
    ],
    ids=["no-skill-md", "no-description", "bad-name"],
)
def test_read_skill_rejects_invalid_folders(tmp_path, front_matter, message):
    folder = tmp_path / "skill"
    folder.mkdir()
    if front_matter is not None:
        (folder / "SKILL.md").write_text(f"---\n{front_matter}\n---\n")

    with pytest.raises(ValueError, match=message.replace("(", r"\(").replace(")", r"\)")):
        read_skill(folder)


def test_write_plugin_links_each_skill(tmp_path):
    entry = read_skill(skill_folder(tmp_path / "skills"))

    plugin = skill.write_plugin([entry], tmp_path / "plugin")

    assert json.loads((plugin / ".claude-plugin" / "plugin.json").read_text())["name"] == "notebook"
    assert os.readlink(plugin / "skills" / "trading-chart") == str(entry.path)
    assert (plugin / "skills" / "trading-chart" / "reference.md").read_text() == "API reference\n"


def test_system_prompt_lists_notebook_skills_only_when_given(tmp_path):
    entry = read_skill(skill_folder(tmp_path))

    with_skills = asyncio.run(system_prompt({}, [entry]))
    without = asyncio.run(system_prompt({}))

    assert with_skills.endswith(
        "## Notebook skills\n\n"
        "These skills document libraries of this notebook that callbacks can import. Before you use one\n"
        "of their APIs, load its skill: with the Skill tool when you have it, otherwise read its SKILL.md\n"
        "and then the files it points to.\n\n"
        f"- `trading-chart`: Draws candles with NotebookChart. (`{entry.path / 'SKILL.md'}`)"
    )
    assert "Notebook skills" not in without


def test_claude_gets_a_plugin_and_read_access_for_each_turn(fake_cli, monkeypatch, tmp_path):
    from test_workbench_agents import FIXTURES, run_turn

    entry = read_skill(skill_folder(tmp_path / "skills"))
    runner = AgentRunner("claude", tmp_path, "sales", skills=[entry])
    monkeypatch.setenv("FAKE_STREAM", str(FIXTURES / "claude" / "first.jsonl"))
    run_turn(runner, "Hi")

    (call,) = fake_cli()
    argv = call["argv"]
    plugin = argv[argv.index("--plugin-dir", argv.index("--plugin-dir") + 1) + 1]
    assert argv[argv.index("--add-dir") + 1] == str(entry.path)
    assert os.path.basename(plugin).startswith("anylumino-skills-")
    assert not os.path.exists(plugin)


def test_workbench_saves_skills_and_keeps_them_on_restore(agent_reply, tmp_path):
    folder = skill_folder(tmp_path / "skills")
    agent_reply(reply("Hello."))
    first = Workbench(agent="codex", session="charts", cwd=tmp_path, skills=[folder])
    first.submit("Hi")

    restored = Workbench(session="charts")

    assert restored.state.skills == [str(folder.resolve())]
    assert restored.skills == [read_skill(folder)]
    (instructions,) = [part for part in agent_reply.calls()[0]["argv"] if part.startswith("developer_instructions=")]
    assert "`trading-chart`: Draws candles with NotebookChart." in json.loads(instructions.split("=", 1)[1])


def test_workbench_rejects_an_invalid_skill_folder(tmp_path):
    with pytest.raises(ValueError, match="is not a skill folder: it has no SKILL.md"):
        Workbench(agent="codex", cwd=tmp_path, skills=[tmp_path])


STATUS_COMPONENTS = '''from anylumino.workbench.catalog import Component, Prop

COMPONENTS = [
    Component(
        "StatusBadge",
        "anylumino.astryx",
        "Badge",
        "A badge for a run status",
        (Prop("label", {"type": "string"}, True),),
    ),
]
'''


def status_skill(root):
    folder = skill_folder(root, "status-badge")
    (folder / "components.py").write_text(STATUS_COMPONENTS)

    return folder


def test_skill_components_join_the_catalog_and_generate_with_their_module(agent_reply, tmp_path):
    import anylumino.astryx as ax

    agent_reply(reply("Done.", 'root = VBox([state])\nstate = StatusBadge("Live", {variant: "success"})'))
    workbench = Workbench(agent="codex", cwd=tmp_path, skills=[status_skill(tmp_path / "skills")])
    workbench.submit("Show the status")

    assert [component.name for component in workbench.skills[0].components] == ["StatusBadge"]
    assert workbench.components[-1].options["variant"]["enum"][:2] == ["neutral", "info"]
    assert "import anylumino.astryx\n" in workbench.ui_code
    assert "self.state = anylumino.astryx.Badge(label='Live', variant='success')" in workbench.ui_code
    assert isinstance(workbench.ui.state, ax.Badge)
    assert (workbench.ui.state.label, workbench.ui.state.variant) == ("Live", "success")


def test_skill_components_reach_the_agent_prompt(tmp_path):
    folder = status_skill(tmp_path)
    workbench = Workbench(agent="codex", cwd=tmp_path, skills=[folder])

    prompt = asyncio.run(system_prompt({}, workbench.skills, workbench.components))

    assert "StatusBadge(label: string" in prompt
    assert "StatusBadge(" not in asyncio.run(system_prompt({}))


def test_a_program_without_the_skill_cannot_use_its_component(agent_reply, tmp_path):
    agent_reply(reply("Done.", 'root = VBox([state])\nstate = StatusBadge("Live")'))
    workbench = Workbench(agent="codex", cwd=tmp_path)
    workbench.submit("Show the status")

    assert workbench.chat.messages[-1]["content"].startswith("The reply was not applied; the UI is unchanged. OpenUI errors:")
    assert workbench.ui is None


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("COMPONENTS = 1\n", "must define COMPONENTS as a sequence of anylumino.workbench.catalog.Component"),
        (
            STATUS_COMPONENTS.replace('"StatusBadge"', '"Heading"'),
            "Component names must be unique; Heading is defined twice",
        ),
    ],
    ids=["not-components", "duplicate-name"],
)
def test_invalid_skill_components_are_rejected(tmp_path, source, message):
    folder = skill_folder(tmp_path)
    (folder / "components.py").write_text(source)

    with pytest.raises(ValueError, match=message):
        Workbench(agent="codex", cwd=tmp_path, skills=[folder])
