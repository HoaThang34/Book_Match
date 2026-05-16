(function () {
  const API_BASE = "";

  function getCookie(name) {
    const match = document.cookie.match(
      new RegExp("(?:^|; )" + name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "=([^;]*)")
    );
    return match ? decodeURIComponent(match[1]) : "";
  }

  function showError(el, message) {
    if (!el) return;
    el.textContent = message || "";
    el.classList.toggle("hidden", !message);
  }

  async function apiPost(path, body) {
    const headers = { "Content-Type": "application/json" };
    const csrf = getCookie("csrf_access_token");
    if (csrf) headers["X-CSRF-TOKEN"] = csrf;

    const response = await fetch(API_BASE + path, {
      method: "POST",
      headers,
      credentials: "include",
      body: JSON.stringify(body),
    });

    let data = {};
    try {
      data = await response.json();
    } catch (_) {
      data = {};
    }
    return { ok: response.ok, status: response.status, data };
  }

  function bindLogin() {
    const form = document.getElementById("login-form");
    if (!form) return;

    const errorEl = document.getElementById("auth-error");
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      showError(errorEl, "");

      const email = document.getElementById("email")?.value?.trim() || "";
      const password = document.getElementById("password")?.value || "";

      const { ok, data } = await apiPost("/api/auth/login", { email, password });
      if (!ok) {
        showError(errorEl, data.error || "Đăng nhập thất bại.");
        return;
      }
      window.location.href = "home.html";
    });
  }

  function bindPasswordToggles() {
    document.querySelectorAll("[data-toggle-password]").forEach(function (btn) {
      var input = document.getElementById(btn.getAttribute("data-toggle-password"));
      if (!input) return;
      var icon = btn.querySelector(".material-symbols-outlined");
      btn.addEventListener("click", function () {
        var show = input.type === "password";
        input.type = show ? "text" : "password";
        if (icon) icon.textContent = show ? "visibility" : "visibility_off";
      });
    });
  }

  function bindLoginExtras() {
    document.querySelectorAll("[data-oauth]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        alert("Tính năng đang phát triển");
      });
    });
    var forgot = document.getElementById("forgot-password");
    if (forgot) {
      forgot.addEventListener("click", function (e) {
        e.preventDefault();
        alert("Vui lòng liên hệ với Quản trị viên");
      });
    }
  }

  function bindSignup() {
    const form = document.getElementById("signup-form");
    if (!form) return;

    const errorEl = document.getElementById("auth-error");
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      showError(errorEl, "");

      const full_name = document.getElementById("full_name")?.value?.trim() || "";
      const email = document.getElementById("email")?.value?.trim() || "";
      const password = document.getElementById("password")?.value || "";
      const confirm_password = document.getElementById("confirm_password")?.value || "";

      const { ok, data } = await apiPost("/api/auth/register", {
        full_name,
        email,
        password,
        confirm_password,
      });
      if (!ok) {
        showError(errorEl, data.error || "Đăng ký thất bại.");
        return;
      }
      window.location.href = "home.html";
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindPasswordToggles();
    bindLoginExtras();
    bindLogin();
    bindSignup();
  });
})();
