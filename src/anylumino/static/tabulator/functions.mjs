// The wire form of `al.JsCode`: an object whose only key is this one.
export const FUNCTION_KEY = "$js";

/**
 * Return `value` with every `{"$js": source}` object replaced by the function
 * its source evaluates to. `path` names the option in error messages, such as
 * `columns[0].formatter`.
 */
export function reviveFunctions(value, path) {
  if (Array.isArray(value)) {
    return value.map((item, index) => reviveFunctions(item, `${path}[${index}]`));
  }
  if (value === null || typeof value !== "object") {
    return value;
  }
  const keys = Object.keys(value);
  if (keys.length === 1 && keys[0] === FUNCTION_KEY && typeof value[FUNCTION_KEY] === "string") {
    return compileFunction(value[FUNCTION_KEY], path);
  }
  return Object.fromEntries(keys.map((key) => [key, reviveFunctions(value[key], `${path}.${key}`)]));
}

export function compileFunction(source, path) {
  let compiled;
  try {
    compiled = new Function(`return (${source}\n);`)();
  } catch (error) {
    throw new Error(`${path}: ${error.message}`);
  }
  if (typeof compiled !== "function") {
    throw new Error(`${path}: the source does not evaluate to a function`);
  }
  return compiled;
}
