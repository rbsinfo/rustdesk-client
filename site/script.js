/* rustdesk-client landing page: language and theme toggles, copy buttons.
   Loaded in <head> so the stored choices apply before the first paint.
   The page is fully readable in English without this script. */
(function () {
  "use strict";

  var root = document.documentElement;
  var LANG_KEY = "rustdesk-client.lang";
  var THEME_KEY = "rustdesk-client.theme";

  function read(key) {
    try {
      return window.localStorage.getItem(key);
    } catch (error) {
      return null;
    }
  }

  function write(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (error) {
      /* Storage is unavailable (private mode, blocked): keep the choice for this page only. */
    }
  }

  function preferredLang() {
    var stored = read(LANG_KEY);
    if (stored === "en" || stored === "fr") {
      return stored;
    }
    var list = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || "en"];
    for (var i = 0; i < list.length; i += 1) {
      var code = String(list[i]).toLowerCase();
      if (code.indexOf("fr") === 0) {
        return "fr";
      }
      if (code.indexOf("en") === 0) {
        return "en";
      }
    }
    return "en";
  }

  function systemDark() {
    return !!(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
  }

  function effectiveTheme() {
    var forced = root.getAttribute("data-theme");
    if (forced === "light" || forced === "dark") {
      return forced;
    }
    return systemDark() ? "dark" : "light";
  }

  var lang = preferredLang();
  var storedTheme = read(THEME_KEY);

  root.classList.remove("no-js");
  root.classList.add("js");
  root.lang = lang;
  root.setAttribute("data-lang", lang);
  if (storedTheme === "light" || storedTheme === "dark") {
    root.setAttribute("data-theme", storedTheme);
  }

  function applyLang(next) {
    lang = next;
    root.lang = next;
    root.setAttribute("data-lang", next);

    var body = document.body;
    if (!body) {
      return;
    }
    var title = body.getAttribute("data-title-" + next);
    if (title) {
      document.title = title;
    }
    var description = document.querySelector('meta[name="description"]');
    if (description && description.getAttribute("data-content-" + next)) {
      description.setAttribute("content", description.getAttribute("data-content-" + next));
    }
    var labelled = document.querySelectorAll("[data-aria-" + next + "]");
    for (var i = 0; i < labelled.length; i += 1) {
      labelled[i].setAttribute("aria-label", labelled[i].getAttribute("data-aria-" + next));
    }
    var buttons = document.querySelectorAll("[data-set-lang]");
    for (var j = 0; j < buttons.length; j += 1) {
      buttons[j].setAttribute("aria-pressed", buttons[j].getAttribute("data-set-lang") === next ? "true" : "false");
    }
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      try {
        if (document.execCommand("copy")) {
          resolve();
        } else {
          reject(new Error("copy refused"));
        }
      } catch (error) {
        reject(error);
      } finally {
        document.body.removeChild(area);
      }
    });
  }

  function ready() {
    applyLang(lang);

    document.addEventListener("click", function (event) {
      var target = event.target.closest ? event.target.closest("button") : null;
      if (!target) {
        return;
      }

      var nextLang = target.getAttribute("data-set-lang");
      if (nextLang === "en" || nextLang === "fr") {
        applyLang(nextLang);
        write(LANG_KEY, nextLang);
        return;
      }

      if (target.id === "theme-toggle") {
        var nextTheme = effectiveTheme() === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", nextTheme);
        write(THEME_KEY, nextTheme);
        return;
      }

      var copyId = target.getAttribute("data-copy");
      if (copyId) {
        var source = document.getElementById(copyId);
        if (!source) {
          return;
        }
        copyText(source.textContent).then(
          function () {
            if (target.classList.contains("is-done")) {
              return;
            }
            var label = target.innerHTML;
            target.classList.add("is-done");
            target.textContent = lang === "fr" ? "Copié" : "Copied";
            window.setTimeout(function () {
              target.classList.remove("is-done");
              target.innerHTML = label;
            }, 1600);
          },
          function () {
            /* Clipboard refused: the text stays selectable in the block. */
          }
        );
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ready);
  } else {
    ready();
  }
})();
