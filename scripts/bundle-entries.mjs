export const shared = {
  bundle: true,
  format: "esm",
  minify: true,
  sourcemap: false,
  target: "es2022",
};

export const entries = [
  ["src/anylumino/static/layout/tab_panel.js", "src/anylumino/static/layout/tab_panel.bundle.js"],
  ["src/anylumino/static/layout/layout_panel.js", "src/anylumino/static/layout/layout_panel.bundle.js"],
  ["src/anylumino/static/layout/action_panel.js", "src/anylumino/static/layout/action_panel.bundle.js"],
  ["src/anylumino/static/controls/native_control_widget.js", "src/anylumino/static/controls/native_control_widget.bundle.js"],
  ["src/anylumino/static/astryx/astryx_widget.js", "src/anylumino/static/astryx/astryx_widget.bundle.js"],
];
