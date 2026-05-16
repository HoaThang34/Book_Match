(function (global) {
  const API_BASE = "";

  function getCookie(name) {
    const match = document.cookie.match(
      new RegExp("(?:^|; )" + name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "=([^;]*)")
    );
    return match ? decodeURIComponent(match[1]) : "";
  }

  function authHeaders() {
    const headers = { "Content-Type": "application/json" };
    const csrf = getCookie("csrf_access_token");
    if (csrf) headers["X-CSRF-TOKEN"] = csrf;
    return headers;
  }

  async function apiRequest(path, options) {
    const response = await fetch(API_BASE + path, {
      credentials: "include",
      ...options,
      headers: { ...authHeaders(), ...(options.headers || {}) },
    });
    let data = {};
    try {
      data = await response.json();
    } catch (_) {
      data = {};
    }
    if (response.status === 401) {
      const err = new Error(data.error || "Yêu cầu đăng nhập.");
      err.status = 401;
      throw err;
    }
    return { ok: response.ok, status: response.status, data };
  }

  global.AppApi = {
    get: (path) => apiRequest(path, { method: "GET" }),
    post: (path, body) =>
      apiRequest(path, { method: "POST", body: JSON.stringify(body || {}) }),
    put: (path, body) =>
      apiRequest(path, { method: "PUT", body: JSON.stringify(body || {}) }),
    getCookie,
  };
})(window);
