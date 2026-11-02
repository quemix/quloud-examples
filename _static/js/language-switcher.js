(function () {
  "use strict";

  const SOURCE_LANGUAGE = "ja";
  const TARGET_LANGUAGE = "en";
  const STORAGE_KEY = "quloud-display-language";
  const JAPANESE_TEXT = /[\u3040-\u30ff\u3400-\u9fff]/;
  const EXCLUDED_SELECTOR = [
    "#quloud-language-switcher",
    "script",
    "style",
    "noscript",
    "code",
    "pre",
    "kbd",
    "samp",
    "textarea",
    ".math",
    ".MathJax",
    ".MathJax_Display",
    "[translate='no']"
  ].join(",");

  let entries = [];
  let originalTitle = document.title;
  let translator = null;
  let translating = false;

  function getPreference() {
    try {
      return localStorage.getItem(STORAGE_KEY) || SOURCE_LANGUAGE;
    } catch (_error) {
      return SOURCE_LANGUAGE;
    }
  }

  function setPreference(language) {
    try {
      localStorage.setItem(STORAGE_KEY, language);
    } catch (_error) {
      // The selector still works for the current page when storage is blocked.
    }
  }

  function collectJapaneseTextNodes() {
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode(node) {
          const parent = node.parentElement;
          if (!parent || parent.closest(EXCLUDED_SELECTOR)) {
            return NodeFilter.FILTER_REJECT;
          }
          if (!JAPANESE_TEXT.test(node.nodeValue || "")) {
            return NodeFilter.FILTER_REJECT;
          }
          return NodeFilter.FILTER_ACCEPT;
        }
      }
    );

    const nodes = [];
    let node;
    while ((node = walker.nextNode())) {
      nodes.push({ node: node, original: node.nodeValue });
    }
    return nodes;
  }

  function restoreJapanese(select, status) {
    for (const entry of entries) {
      if (entry.node.isConnected) {
        entry.node.nodeValue = entry.original;
      }
    }
    document.title = originalTitle;
    document.documentElement.lang = SOURCE_LANGUAGE;
    select.value = SOURCE_LANGUAGE;
    status.textContent = "日本語（原文）";
    setPreference(SOURCE_LANGUAGE);
    if (translator && typeof translator.destroy === "function") {
      translator.destroy();
    }
    translator = null;
  }

  function updateProgress(status, loaded) {
    const percent = Math.max(0, Math.min(100, Math.round(loaded * 100)));
    status.textContent = "翻訳モデルを準備中… " + percent + "%";
  }

  async function translateToEnglish(select, status, userInitiated) {
    if (translating) {
      return;
    }

    if (!("Translator" in globalThis)) {
      select.value = SOURCE_LANGUAGE;
      status.textContent = "英訳にはChrome 138以降のデスクトップ版が必要です。";
      setPreference(SOURCE_LANGUAGE);
      return;
    }

    translating = true;
    select.disabled = true;
    status.textContent = "English translationを準備中…";

    try {
      // When initiated by the selector, create() is called before the first
      // await so Chrome can associate a model download with the user action.
      const createPromise = globalThis.Translator.create({
        sourceLanguage: SOURCE_LANGUAGE,
        targetLanguage: TARGET_LANGUAGE,
        monitor(monitor) {
          monitor.addEventListener("downloadprogress", function (event) {
            updateProgress(status, event.loaded);
          });
        }
      });

      translator = await createPromise;
      const total = entries.length;
      for (let index = 0; index < total; index += 1) {
        const entry = entries[index];
        if (!entry.node.isConnected) {
          continue;
        }
        entry.node.nodeValue = await translator.translate(entry.original);
        if (index % 5 === 0 || index + 1 === total) {
          status.textContent = "翻訳中… " + (index + 1) + "/" + total;
        }
      }

      if (JAPANESE_TEXT.test(originalTitle)) {
        document.title = await translator.translate(originalTitle);
      }
      document.documentElement.lang = TARGET_LANGUAGE;
      select.value = TARGET_LANGUAGE;
      status.textContent = "English（ブラウザーAI自動翻訳）";
      setPreference(TARGET_LANGUAGE);
    } catch (error) {
      restoreJapanese(select, status);
      status.textContent = userInitiated
        ? "英訳を開始できませんでした。対応ブラウザーとHTTPS接続を確認してください。"
        : "Englishを選択すると、このページを翻訳できます。";
      console.warn("Quloud translation unavailable:", error);
    } finally {
      translating = false;
      select.disabled = false;
    }
  }

  function createLanguageSwitcher() {
    const sidebarHeader = document.querySelector(".wy-side-nav-search");
    if (!sidebarHeader || document.getElementById("quloud-language-switcher")) {
      return;
    }

    const wrapper = document.createElement("div");
    wrapper.id = "quloud-language-switcher";
    wrapper.className = "quloud-language-switcher";
    wrapper.setAttribute("translate", "no");

    const label = document.createElement("label");
    label.htmlFor = "quloud-language-select";
    label.textContent = "表示言語 / Language";

    const select = document.createElement("select");
    select.id = "quloud-language-select";
    select.setAttribute("aria-label", "表示言語 / Display language");
    select.innerHTML =
      '<option value="ja">日本語</option>' +
      '<option value="en">English</option>';

    const status = document.createElement("span");
    status.className = "quloud-language-status";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    status.textContent = "日本語（原文）";

    wrapper.appendChild(label);
    wrapper.appendChild(select);
    wrapper.appendChild(status);

    const search = sidebarHeader.querySelector("[role='search']");
    sidebarHeader.insertBefore(wrapper, search || null);

    entries = collectJapaneseTextNodes();
    originalTitle = document.title;

    select.addEventListener("change", function () {
      if (select.value === TARGET_LANGUAGE) {
        translateToEnglish(select, status, true);
      } else {
        restoreJapanese(select, status);
      }
    });

    if (getPreference() === TARGET_LANGUAGE) {
      select.value = TARGET_LANGUAGE;
      translateToEnglish(select, status, false);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", createLanguageSwitcher);
  } else {
    createLanguageSwitcher();
  }
})();
