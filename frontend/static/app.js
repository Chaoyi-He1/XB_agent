(function () {
  const API_BASE = "";

  const messagesEl = document.getElementById("messages");
  const welcomeEl = document.getElementById("welcome");
  const chatForm = document.getElementById("chatForm");
  const inputEl = document.getElementById("input");
  const sendBtn = document.getElementById("sendBtn");
  const settingsBtn = document.getElementById("settingsBtn");
  const settingsModal = document.getElementById("settingsModal");
  const settingsForm = document.getElementById("settingsForm");
  const modalCancel = document.getElementById("modalCancel");

  function getApiConfig() {
    return {
      api_url: document.getElementById("apiUrl").value.trim() || undefined,
      api_key: document.getElementById("apiKey").value.trim() || undefined,
      model_name: document.getElementById("modelName").value.trim() || undefined,
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

    const payload = { message: text.trim(), ...getApiConfig() };

    try {
      const res = await fetch(API_BASE + "/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));

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

  settingsBtn.addEventListener("click", function () {
    settingsModal.showModal();
  });

  modalCancel.addEventListener("click", function () {
    settingsModal.close();
  });

  settingsForm.addEventListener("submit", function (e) {
    e.preventDefault();
    settingsModal.close();
  });

  settingsModal.addEventListener("click", function (e) {
    if (e.target === settingsModal) settingsModal.close();
  });
})();
