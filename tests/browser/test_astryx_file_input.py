def test_file_input_shows_the_chosen_file(notebook, tmp_path):
    report = tmp_path / "report.csv"
    report.write_text("a,b\n1,2\n")
    nb = notebook("import anylumino.astryx as ax\nfiles = ax.FileInput(label='Upload')\nfiles")
    output = nb.output(0)
    picker = output.locator("input[type=file]")
    picker.wait_for(state="attached")

    picker.set_input_files(str(report))
    output.get_by_text("report.csv").wait_for()
    nb.page.wait_for_timeout(500)

    assert nb.value("files.value['name']") == "report.csv"
    assert nb.value("files.value['size']") == 8
