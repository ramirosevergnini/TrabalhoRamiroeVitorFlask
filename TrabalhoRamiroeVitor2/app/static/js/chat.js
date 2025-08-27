(function () {
  if (typeof io === "undefined") return;
  const socket = io();

  const box = document.getElementById("chat-box");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");

  function scrollBottom() {
    if (box) box.scrollTop = box.scrollHeight;
  }

  socket.on("connect", () => {
    socket.emit("join", { room_id: ROOM_ID, token: TOKEN });
  });

  socket.on("system", (data) => {
    const div = document.createElement("div");
    div.className = "text-muted small";
    div.textContent = data.message;
    box.appendChild(div);
    scrollBottom();
  });

  socket.on("new_message", (data) => {
    const div = document.createElement("div");
    div.innerHTML = "<strong>" + data.user + ":</strong> " + data.text + " <span class='text-muted small'>" + data.at.substring(11,16) + "</span>";
    box.appendChild(div);
    scrollBottom();
  });

  socket.on("banned", (data) => {
    alert(data.message || "Banido desta sala.");
  });

  socket.on("error", (data) => {
    alert(data.message || "Erro no chat.");
  });

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const text = (input.value || "").trim();
      if (!text) return;
      socket.emit("send_message", { room_id: ROOM_ID, text });
      input.value = "";
    });
  }
})();
