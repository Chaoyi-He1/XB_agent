(function () {
  const API_BASE = "";
  const SESSION_STORAGE_KEY = "memristor_chat_session_id";

  const messagesEl = document.getElementById("messages");
  const welcomeEl = document.getElementById("welcome");
  const chatForm = document.getElementById("chatForm");
  const inputEl = document.getElementById("input");
  const modelSelect = document.getElementById("modelSelect");
  const sessionListEl = document.getElementById("sessionList");
  const newChatBtn = document.getElementById("newChatBtn");
  const searchChatsEl = document.getElementById("searchChats");
  let sessionId = localStorage.getItem(SESSION_STORAGE_KEY) || "";
  let sessionListData = [];

  const DEFAULT_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"];

  function filterSessionList() {
    const q = (searchChatsEl && searchChatsEl.value) ? searchChatsEl.value.trim().toLowerCase() : "";
    sessionListEl.querySelectorAll(".session-item").forEach(function (el) {
      const title = (el.textContent || "").toLowerCase();
      el.classList.toggle("hidden", q && title.indexOf(q) === -1);
    });
  }

  async function loadSessions() {
    try {
      const res = await fetch(API_BASE + "/api/sessions");
      const list = await res.json().catch(() => []);
      sessionListData = Array.isArray(list) ? list : [];
      sessionListEl.innerHTML = "";
      sessionListData.forEach(function (s) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "session-item" + (s.id === sessionId ? " active" : "");
        btn.textContent = s.title || "New chat";
        btn.dataset.sessionId = s.id;
        btn.addEventListener("click", function () {
          selectSession(s.id);
        });
        sessionListEl.appendChild(btn);
      });
      filterSessionList();
    } catch (e) {
      sessionListEl.innerHTML = "";
    }
  }

  if (searchChatsEl) {
    searchChatsEl.addEventListener("input", filterSessionList);
  }

  function selectSession(id) {
    sessionId = id || "";
    if (sessionId) localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
    else localStorage.removeItem(SESSION_STORAGE_KEY);
    sessionListEl.querySelectorAll(".session-item").forEach(function (el) {
      el.classList.toggle("active", el.dataset.sessionId === sessionId);
    });
    if (!id) {
      clearMessages();
      if (welcomeEl) welcomeEl.style.display = "";
      return;
    }
    fetch(API_BASE + "/api/sessions/" + encodeURIComponent(id))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        clearMessages();
        (data.messages || []).forEach(function (m) {
          addMessage(m.role, m.content, false, false);
        });
        if (welcomeEl) welcomeEl.style.display = (data.messages && data.messages.length) ? "none" : "";
      })
      .catch(function () {
        clearMessages();
        if (welcomeEl) welcomeEl.style.display = "";
      });
  }

  function clearMessages() {
    const welcome = document.getElementById("welcome");
    messagesEl.innerHTML = "";
    if (welcome) {
      messagesEl.appendChild(welcome);
    }
  }

  newChatBtn.addEventListener("click", function () {
    selectSession(null);
  });

  async function loadModelList() {
    try {
      const res = await fetch(API_BASE + "/api/models");
      const data = await res.json().catch(() => ({}));
      const models = Array.isArray(data.models) && data.models.length ? data.models : DEFAULT_MODELS;
      const defaultModel = data.default && models.includes(data.default) ? data.default : models[0];
      modelSelect.innerHTML = "";
      models.forEach(function (m) {
        const opt = document.createElement("option");
        opt.value = m;
        opt.textContent = m;
        if (m === defaultModel) opt.selected = true;
        modelSelect.appendChild(opt);
      });
    } catch (e) {
      modelSelect.innerHTML = "";
      DEFAULT_MODELS.forEach(function (m) {
        const opt = document.createElement("option");
        opt.value = m;
        opt.textContent = m;
        if (m === "gpt-4o-mini") opt.selected = true;
        modelSelect.appendChild(opt);
      });
    }
  }

  loadModelList();
  loadSessions();

  function getPayload() {
    return {
      message: "",
      session_id: sessionId || undefined,
      model_name: modelSelect ? modelSelect.value : undefined,
    };
  }

  function hideWelcome() {
    if (welcomeEl) welcomeEl.style.display = "none";
  }

  function addMessage(role, content, isError = false, isLoading = false) {
    hideWelcome();
    const div = document.createElement("div");
    div.className = "msg " + role + (isError ? " error" : "") + (isLoading ? " loading" : "");
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = role === "user" ? "You" : "AI";
    const body = document.createElement("div");
    body.className = "body";
    body.textContent = content;
    div.appendChild(avatar);
    div.appendChild(body);
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return body;
  }

  async function sendMessage(text) {
    if (!text.trim()) return;
    addMessage("user", text.trim());
    inputEl.value = "";
    inputEl.style.height = "auto";

    const loadingBodyEl = addMessage("assistant", "Thinking…", false, true);
    const loadingMsg = loadingBodyEl && loadingBodyEl.closest ? loadingBodyEl.closest(".msg") : messagesEl.querySelector(".msg.loading");

    const payload = { ...getPayload(), message: text.trim() };
    if (!sessionId) payload.session_id = null;

    try {
      const res = await fetch(API_BASE + "/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (data.session_id) {
        sessionId = data.session_id;
        localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
        if (data.session_title) {
          loadSessions();
          sessionListEl.querySelectorAll(".session-item").forEach(function (el) {
            el.classList.toggle("active", el.dataset.sessionId === sessionId);
          });
        }
      }

      if (loadingBodyEl) {
        loadingMsg.classList.remove("loading");
        if (!res.ok) {
          loadingMsg.classList.add("error");
          loadingBodyEl.textContent = data.detail || data.message || "Request failed.";
          return;
        }
        loadingBodyEl.textContent = data.reply || "No reply.";
      }
    } catch (err) {
      if (loadingBodyEl) {
        loadingMsg.classList.remove("loading");
        loadingMsg.classList.add("error");
        loadingBodyEl.textContent = "Network error: " + (err.message || "Could not reach server.");
      }
    }
  }

  chatForm.addEventListener("submit", function (e) {
    e.preventDefault();
    sendMessage(inputEl.value);
  });

  inputEl.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.requestSubmit();
    }
  });

  inputEl.addEventListener("input", function () {
    inputEl.style.height = "auto";
    inputEl.style.height = Math.min(inputEl.scrollHeight, 200) + "px";
  });
})();
