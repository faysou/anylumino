import assert from "node:assert/strict";
import test from "node:test";

import { claimDocumentTheme, claimThemeCSS } from "../../src/anylumino/static/astryx/astryx_theme.mjs";


class FakeElement {
  constructor(tagName) {
    this.tagName = tagName;
    this.attributes = new Map();
    this.children = [];
    this.textContent = "";
    this.isConnected = false;
    this.parent = null;
  }

  setAttribute(name, value) {
    this.attributes.set(name, String(value));
    this.onAttributeChanged?.();
  }

  getAttribute(name) {
    return this.attributes.has(name) ? this.attributes.get(name) : null;
  }

  removeAttribute(name) {
    this.attributes.delete(name);
    this.onAttributeChanged?.();
  }

  appendChild(child) {
    this.children.push(child);
    child.isConnected = true;
    child.parent = this;
    return child;
  }

  remove() {
    const index = this.parent?.children.indexOf(this) ?? -1;
    if (index >= 0) {
      this.parent.children.splice(index, 1);
    }
    this.isConnected = false;
  }
}


class FakeDocument {
  constructor() {
    this.head = new FakeElement("head");
    this.documentElement = new FakeElement("html");
  }

  createElement(tagName) {
    return new FakeElement(tagName);
  }

  querySelectorAll(selector) {
    const match = /^style\[([^=]+)="([^"]+)"\]$/.exec(selector);
    return this.head.children.filter((child) => child.getAttribute(match[1]) === match[2]);
  }
}


test("claimThemeCSS shares one style tag and only removes it on the last release", () => {
  const documentRef = new FakeDocument();
  const css = ":root { --color-accent: #0057b8; }";

  const releaseFirst = claimThemeCSS("desk", css, documentRef);
  const releaseSecond = claimThemeCSS("desk", css, documentRef);

  assert.equal(documentRef.head.children.length, 1);
  const style = documentRef.head.children[0];
  assert.equal(style.textContent, css);
  assert.equal(style.getAttribute("data-anylumino-astryx-theme"), "desk");
  assert.equal(style.getAttribute("data-anylumino-astryx-theme-count"), "2");

  releaseFirst();

  assert.equal(documentRef.head.children.length, 1);
  assert.equal(style.getAttribute("data-anylumino-astryx-theme-count"), "1");

  releaseSecond();

  assert.equal(documentRef.head.children.length, 0);
});


test("claimThemeCSS keeps distinct stylesheets apart and ignores empty CSS", () => {
  const documentRef = new FakeDocument();

  const releaseBlue = claimThemeCSS("desk", ":root { --color-accent: #0057b8; }", documentRef);
  const releaseGreen = claimThemeCSS("desk", ":root { --color-accent: #0f7b43; }", documentRef);
  const releaseEmpty = claimThemeCSS("desk", "   ", documentRef);

  assert.equal(documentRef.head.children.length, 2);
  assert.equal(
    new Set(documentRef.head.children.map((child) => child.getAttribute("data-anylumino-astryx-theme-id"))).size,
    2,
  );

  releaseEmpty();
  releaseBlue();
  releaseGreen();

  assert.equal(documentRef.head.children.length, 0);
});


test("claimThemeCSS appends to a shadow root instead of the document head", () => {
  const documentRef = new FakeDocument();
  const shadowRoot = new FakeElement("#shadow-root");
  shadowRoot.ownerDocument = documentRef;
  shadowRoot.querySelectorAll = (selector) => {
    const match = /^style\[([^=]+)="([^"]+)"\]$/.exec(selector);
    return shadowRoot.children.filter((child) => child.getAttribute(match[1]) === match[2]);
  };
  const css = ":root { --color-accent: #0057b8; }";

  const releaseFirst = claimThemeCSS("desk", css, shadowRoot);
  const releaseSecond = claimThemeCSS("desk", css, shadowRoot);

  assert.equal(documentRef.head.children.length, 0);
  assert.equal(shadowRoot.children.length, 1);
  const style = shadowRoot.children[0];
  assert.equal(style.textContent, css);
  assert.equal(style.getAttribute("data-anylumino-astryx-theme"), "desk");
  assert.equal(style.getAttribute("data-anylumino-astryx-theme-count"), "2");

  releaseFirst();
  releaseSecond();

  assert.equal(shadowRoot.children.length, 0);
});


test("claimDocumentTheme restores the host page mode once the last widget releases", () => {
  const documentRef = new FakeDocument();
  documentRef.documentElement.setAttribute("data-theme", "light");

  const releaseFirst = claimDocumentTheme(documentRef);
  const releaseSecond = claimDocumentTheme(documentRef);

  // Astryx keeps deciding the page attribute while widgets are mounted; policing
  // it would restyle the whole document on every write.
  documentRef.documentElement.setAttribute("data-theme", "dark");
  releaseFirst();
  assert.equal(documentRef.documentElement.getAttribute("data-theme"), "dark");

  // The last release restores what the host page started with, so unmounting one
  // output does not leave the page without a mode.
  releaseSecond();
  assert.equal(documentRef.documentElement.getAttribute("data-theme"), "light");
});


test("claimDocumentTheme leaves a page that had no mode attribute unset", () => {
  const documentRef = new FakeDocument();

  const release = claimDocumentTheme(documentRef);
  documentRef.documentElement.setAttribute("data-theme", "dark");
  release();

  assert.equal(documentRef.documentElement.getAttribute("data-theme"), null);
});


test("claimDocumentTheme releases are idempotent", () => {
  const documentRef = new FakeDocument();
  documentRef.documentElement.setAttribute("data-theme", "light");

  const release = claimDocumentTheme(documentRef);
  documentRef.documentElement.setAttribute("data-theme", "dark");
  release();
  release();
  documentRef.documentElement.setAttribute("data-theme", "dark");

  assert.equal(documentRef.documentElement.getAttribute("data-theme"), "dark");
});
