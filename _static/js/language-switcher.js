(function () {
  "use strict";

  const LANGUAGE_PAIR = { sourceLanguage: "ja", targetLanguage: "en" };
  const STORAGE_KEY = "quloud-display-language";
  const JAPANESE_TEXT = /[\u3040-\u30ff\u3400-\u9fff]/;
  const EXCLUDED_SELECTOR = [
    "script", "style", "noscript", "code", "pre", "kbd", "samp", "textarea", "sub", "sup",
    ".math", ".MathJax", "mjx-container", "[translate='no']"
  ].join(",");
  const INLINE_ELEMENTS = "a, abbr, b, cite, code, em, i, kbd, mark, samp, small, span, strong, sub, sup, var, mjx-container";
  const INLINE_MATH = "span.math, span.MathJax, mjx-container:not([display='true'])";
  const SCRIPT_ELEMENT = "sub, sup";
  const CJK_PUNCTUATION = /[、。，：；（）〜～]/;
  const ENGLISH_PUNCTUATION = {
    "、": ",", "。": ".", "，": ",", "：": ":", "；": ";", "（": "(", "）": ")", "〜": "–", "～": "–"
  };
  // The last four entries cover the landing pages, whose short descriptions list terms
  // that the translator gets wrong without context. check_en_table.py parses this list as JSON.
  const FIXED_LABEL_SELECTORS = [
    ".navbar-brand .logo__title",
    ".navbar-header-items__center a",
    ".sidebar-header-items__center a",
    ".search-button__default-text",
    ".pst-collapse-sidebar-label",
    ".pst-expand-sidebar-label",
    ".bd-docs-nav a",
    ".bd-links__title:not(:has(a))",
    ".bd-docs-nav .caption-text",
    ".onthispage",
    "nav.page-toc a",
    ".breadcrumb-item:not(.breadcrumb-home) > a",
    ".breadcrumb-item.active > .ellipsis",
    ".prev-next-subtitle",
    ".prev-next-title",
    "article a.reference.internal",
    "article h1", "article h2", "article h3", "article h4",
    "article p:has(+ .book-list)", ".book-list li > p:not(:has(a))",
    "article p:has(+ .case-list)", ".case-list li > p:not(:has(a))"
  ];
  const FIXED_LABEL_SELECTOR = FIXED_LABEL_SELECTORS.join(",");
  const SECTION_NUMBER = /^\d+(?:\.\d+)*\.?\s+/;
  const LATIN_TOKEN = /[A-Za-z0-9_₀-₉]+(?:-[A-Za-z0-9_₀-₉]+)*/g;

  async function loadEnglishLabels() {
    const root = document.documentElement.dataset.content_root || "./";
    try {
      const url = new URL(root + "_static/translations/en.json", document.baseURI);
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return new Map(Object.entries(await response.json()));
    } catch (error) {
      console.warn("Quloud English labels unavailable:", error);
      return new Map();
    }
  }

  function collectFixedLabels(table) {
    const labels = new Map();
    for (const element of document.querySelectorAll(FIXED_LABEL_SELECTOR)) {
      const copy = element.cloneNode(true);
      const numbers = Array.from(copy.querySelectorAll(".section-number"));
      const permalinks = Array.from(copy.querySelectorAll(".headerlink"));
      // Use the TeX from Sphinx even after MathJax has rendered an inline formula.
      const mathDocument = globalThis.MathJax?.startup?.document;
      if (mathDocument && copy.querySelector("mjx-container")) {
        const math = Array.from(mathDocument.getMathItemsWithin(element));
        math.forEach((item, index) => {
          const formula = copy.querySelectorAll("mjx-container")[index];
          if (formula && !item.display) {
            formula.replaceWith(`\\(${item.math}\\)`);
          }
        });
      }
      for (const decoration of [...numbers, ...permalinks]) {
        decoration.remove();
      }
      const text = copy.textContent.trim().replace(/\s+/g, " ");
      const prefix = text.match(SECTION_NUMBER)?.[0] ?? "";
      const english = table.get(text.slice(prefix.length));
      if (english) {
        const reference = copy.querySelector(":scope > :is(.std-ref, .std-numref, .doc)");
        const translated = reference?.textContent.trim().replace(/\s+/g, " ") === text ? reference : null;
        if (translated) {
          translated.textContent = prefix + english;
        }
        labels.set(element, {
          original: Array.from(element.childNodes),
          english: [...numbers, translated ?? prefix + english, ...permalinks]
        });
      }
    }
    return labels;
  }

  function restoreLatinCase(original, translated) {
    const forms = new Map();
    for (const token of original.matchAll(LATIN_TOKEN)) {
      const word = token[0];
      const key = word.toLowerCase();
      forms.set(key, !forms.has(key) || forms.get(key) === word ? word : null);
    }
    return translated.replace(LATIN_TOKEN, (word, offset) => {
      const originalWord = forms.get(word.toLowerCase());
      if (!originalWord || originalWord.length < 2 || !/[a-z]/.test(originalWord)) {
        return word;
      }
      if (originalWord === originalWord.toLowerCase()
          && word === originalWord[0].toUpperCase() + originalWord.slice(1)
          && /(?:^|[.!?])\s*$/.test(translated.slice(0, offset))) {
        return word;
      }
      return originalWord;
    });
  }

  function readPreference() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch {
      return null;
    }
  }

  function savePreference(language) {
    try {
      localStorage.setItem(STORAGE_KEY, language);
    } catch {
      // Translation still works for the current page when storage is blocked.
    }
  }

  function collectJapaneseTextNodes(fixedLabels) {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        return (JAPANESE_TEXT.test(node.nodeValue) || CJK_PUNCTUATION.test(node.nodeValue))
          && !node.parentElement.closest(EXCLUDED_SELECTOR)
          && !fixedLabels.has(node.parentElement.closest(FIXED_LABEL_SELECTOR))
          ? NodeFilter.FILTER_ACCEPT
          : NodeFilter.FILTER_REJECT;
      }
    });

    const entries = [];
    while (walker.nextNode()) {
      const node = walker.currentNode;
      entries.push({ node, original: node.nodeValue });
    }
    return entries;
  }

  function adjacentInlineContent(node, sibling, child) {
    while (!node[sibling]) {
      node = node.parentElement;
      if (!node?.matches(INLINE_ELEMENTS)) {
        return null;
      }
    }

    node = node[sibling];
    while (node?.nodeType === Node.ELEMENT_NODE && node.matches(INLINE_ELEMENTS)) {
      if (node.matches(`${SCRIPT_ELEMENT}, ${INLINE_MATH}`)) {
        return node;
      }
      node = node[child];
    }
    return node?.nodeType === Node.TEXT_NODE ? node : null;
  }

  function isScript(node) {
    return node?.nodeType === Node.ELEMENT_NODE && node.matches(SCRIPT_ELEMENT);
  }

  function needsSpace(left, right, translations) {
    if (!left || !right || isScript(right)) {
      return false;
    }
    if (isScript(left) && right.nodeType === Node.TEXT_NODE && /^[A-Za-z0-9]/.test(right.nodeValue)) {
      // Keep a formula joined if the original text continues directly after the script.
      return false;
    }
    // Treat an inline equation or script as a word at its outer boundary.
    const leftText = translations.get(left) ?? left.nodeValue ?? "0";
    const rightText = translations.get(right) ?? right.nodeValue ?? "0";
    return /[\p{L}\p{N}.,;:!?\])%]$/u.test(leftText) && /^[\p{L}\p{N}([]/u.test(rightText);
  }

  async function translateText({ node, original }, translator) {
    // Leave the original whitespace and any symbol attached to a script intact.
    const [, before, text, after] = original.match(/^(\s*)(.*?)(\s*)$/s);
    const previous = adjacentInlineContent(node, "previousSibling", "lastChild");
    const next = adjacentInlineContent(node, "nextSibling", "firstChild");
    const prefix = !before && isScript(previous) ? text.match(/^[A-Za-z0-9]+/)?.[0] ?? "" : "";
    const suffix = !after && isScript(next) ? text.match(/[A-Za-z0-9]+$/)?.[0] ?? "" : "";
    const body = text.slice(prefix.length, text.length - suffix.length);
    // Text between links can be only Japanese punctuation, which the translator never sees.
    const translated = JAPANESE_TEXT.test(body)
      ? restoreLatinCase(body, await translator.translate(body))
      : body.replace(/[、。，：；（）〜～]/g, (c) => ENGLISH_PUNCTUATION[c]);
    return before + [prefix, translated.trim(), suffix].filter(Boolean).join(" ") + after;
  }

  function addEnglishSpacing(translations) {
    for (const [node, text] of translations) {
      const previous = adjacentInlineContent(node, "previousSibling", "lastChild");
      const next = adjacentInlineContent(node, "nextSibling", "firstChild");
      // When both sides are translated, only the left node adds the space.
      const before = !translations.has(previous) && needsSpace(previous, node, translations) ? " " : "";
      const after = needsSpace(node, next, translations) ? " " : "";
      translations.set(node, before + text + after);
    }
  }

  async function checkAvailability(api) {
    let timeout;
    try {
      return await Promise.race([
        api.availability(LANGUAGE_PAIR),
        new Promise((resolve) => {
          timeout = setTimeout(resolve, 5000, "unavailable");
        })
      ]);
    } catch {
      return "unavailable";
    } finally {
      clearTimeout(timeout);
    }
  }

  async function initialize() {
    // PyData renders navbar_end in both the desktop header and the mobile menu.
    const controls = Array.from(document.querySelectorAll(".quloud-language-switcher"), (menu) => ({
      menu,
      toggle: menu.querySelector(".dropdown-toggle"),
      japanese: menu.querySelector("[data-language='ja']"),
      english: menu.querySelector("[data-language='en']"),
      statusJa: menu.querySelector(".quloud-language-status [lang='ja']"),
      statusEn: menu.querySelector(".quloud-language-status [lang='en']")
    }));
    if (!controls.length) {
      return;
    }

    const api = globalThis.Translator;
    const englishLabels = loadEnglishLabels();
    const originalTitle = document.title;
    let entries = [];
    let fixedLabels = new Map();
    const translationNote = document.createElement("p");
    translationNote.className = "quloud-translation-note";
    translationNote.setAttribute("translate", "no");
    translationNote.textContent = "This page was machine-translated in your browser. Technical terms may be inaccurate; the Japanese original is authoritative.";
    let currentLanguage = "ja";
    let busy = false;
    let supported = false;

    function showStatus(japanese = "", english = "") {
      for (const control of controls) {
        control.statusJa.textContent = japanese;
        control.statusEn.textContent = english;
      }
    }

    function setBusy(value) {
      busy = value;
      for (const control of controls) {
        control.japanese.disabled = value;
        control.english.disabled = value || !supported;
        control.toggle.querySelector(".fa-language").hidden = value;
        control.toggle.querySelector(".spinner-border").hidden = !value;
      }
    }

    function setLanguage(language) {
      currentLanguage = language;
      document.documentElement.lang = language;
      for (const control of controls) {
        for (const option of [control.japanese, control.english]) {
          if (option.dataset.language === language) {
            option.setAttribute("aria-current", "true");
          } else {
            option.removeAttribute("aria-current");
          }
        }
      }
      savePreference(language);
    }

    async function translateToEnglish() {
      if (busy || currentLanguage === "en") {
        return;
      }
      setBusy(true);
      showStatus("翻訳を準備中…", "Preparing translation…");
      let translator;
      let loadingModel = true;
      try {
        // Call create() before the first await to retain the user's activation.
        translator = await api.create({
          ...LANGUAGE_PAIR,
          monitor(monitor) {
            monitor.addEventListener("downloadprogress", (event) => {
              if (loadingModel) {
                const percent = Math.round(event.loaded * 100);
                showStatus(`翻訳モデルを準備中… ${percent}%`, `Preparing translation model… ${percent}%`);
              }
            });
          }
        });
        loadingModel = false;
        fixedLabels = collectFixedLabels(await englishLabels);
        entries = collectJapaneseTextNodes(fixedLabels);
        const translations = new Map();
        let progress = 0;
        showStatus("翻訳中… 0%", "Translating… 0%");
        for (const entry of entries) {
          translations.set(entry.node, await translateText(entry, translator));
          const percent = 10 * Math.floor(10 * translations.size / entries.length);
          if (percent > progress && percent < 100) {
            progress = percent;
            showStatus(`翻訳中… ${progress}%`, `Translating… ${progress}%`);
          }
        }
        const title = JAPANESE_TEXT.test(originalTitle)
          ? await translator.translate(originalTitle)
          : originalTitle;
        // Inline links can begin or end with different characters in the fixed English labels.
        for (const [element, label] of fixedLabels) {
          element.replaceChildren(...label.english);
        }
        addEnglishSpacing(translations);
        for (const [node, text] of translations) {
          node.nodeValue = text;
        }
        document.querySelector("article")?.prepend(translationNote);
        document.title = title;
        setLanguage("en");
        showStatus("", "Machine translation shown. Terms may be inaccurate.");
      } catch (error) {
        showStatus(
          "翻訳できませんでした。もう一度 English を選ぶか、ブラウザーのページ翻訳機能をお使いください。",
          "Translation failed. Select English again, or use your browser’s page translation."
        );
        console.warn("Quloud translation unavailable:", error);
      } finally {
        loadingModel = false;
        translator?.destroy();
        setBusy(false);
      }
    }

    for (const control of controls) {
      // Match PyData's color control and keep the tooltip out of the open dropdown.
      control.menu.addEventListener("show.bs.dropdown", () => {
        const tooltip = globalThis.bootstrap?.Tooltip.getInstance(control.menu);
        tooltip?.hide();
        tooltip?.disable();
      });
      control.menu.addEventListener("hide.bs.dropdown", () => {
        globalThis.bootstrap?.Tooltip.getInstance(control.menu)?.enable();
      });
      control.english.addEventListener("click", () => {
        if (currentLanguage === "ja") {
          control.toggle.focus();
          translateToEnglish();
        }
      });
      control.japanese.addEventListener("click", () => {
        if (currentLanguage === "en") {
          for (const { node, original } of entries) {
            node.nodeValue = original;
          }
          entries = [];
          for (const [element, label] of fixedLabels) {
            element.replaceChildren(...label.original);
          }
          fixedLabels.clear();
          translationNote.remove();
          document.title = originalTitle;
          showStatus("日本語の原文に戻しました。");
        }
        setLanguage("ja");
      });
      control.menu.hidden = false;
    }

    let availability = "unavailable";
    if (globalThis.isSecureContext && typeof api?.availability === "function") {
      showStatus("自動翻訳の利用可否を確認中…", "Checking translation availability…");
      availability = await checkAvailability(api);
    }
    supported = ["available", "downloadable", "downloading"].includes(availability);
    setBusy(false);
    showStatus();
    if (!supported) {
      showStatus(
        "この環境では自動翻訳を利用できません。ブラウザーのページ翻訳機能を使うか、対応するパソコン版 Chrome などで開いてください。",
        "Automatic translation is unavailable here. Use your browser’s page translation, or open in a supported desktop browser such as Chrome."
      );
    } else if (readPreference() === "en") {
      if (availability === "available") {
        translateToEnglish();
      } else {
        showStatus("English を選ぶと翻訳を開始します。", "Select English to start translation.");
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize);
  } else {
    initialize();
  }
})();
