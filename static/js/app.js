(function () {
  const api = window.AppApi;
  if (!api) return;

  const PLACEHOLDER_COVER =
    "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600&h=800&fit=crop";

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s || "";
    return d.innerHTML;
  }

  function streakLabel(days) {
    return days === 1 ? "1 Day" : days + " Days";
  }

  async function loadHeaderStreak() {
    const els = document.querySelectorAll("[data-streak-badge]");
    if (!els.length) return;
    try {
      const { ok, data } = await api.get("/api/user/stats");
      if (!ok) return;
      const n = data.stats?.current_streak ?? 0;
      const text = streakLabel(n);
      els.forEach(function (el) {
        const inner = el.querySelector("[data-streak-text]");
        if (inner) inner.textContent = text;
        else el.textContent = text + " \u2728";
      });
    } catch (e) {
      if (e.status === 401) els.forEach(function (el) { el.style.display = "none"; });
    }
  }

  function renderRecommendationCard(b) {
    const pct = b.match_percent || 85;
    return (
      '<article class="bg-surface-container-lowest rounded-xl overflow-hidden shadow-sm border border-outline-variant/30">' +
      '<div class="h-64 w-full bg-surface-variant relative">' +
      '<img alt="' + escapeHtml(b.title) + '" class="w-full h-full object-cover opacity-90" src="' + PLACEHOLDER_COVER + '">' +
      '<div class="absolute inset-0 bg-gradient-to-t from-surface-container-lowest via-transparent to-transparent"></div>' +
      '<div class="absolute top-4 right-4 bg-primary-container text-on-primary-container font-label-lg px-3 py-1 rounded-full shadow-md">' + pct + '% AI Match</div>' +
      '</div>' +
      '<div class="p-6 relative z-10 -mt-12 bg-surface-container-lowest/95 backdrop-blur-xl rounded-t-xl border-t border-outline-variant/20">' +
      '<h3 class="font-headline-md text-on-surface mb-1">' + escapeHtml(b.title) + '</h3>' +
      '<p class="font-body-md text-on-surface-variant mb-4">' + escapeHtml(b.author) + '</p>' +
      '<p class="font-body-md text-on-surface/90 line-clamp-3 mb-6">' + escapeHtml(b.description) + '</p>' +
      '<div class="bg-surface-container border border-outline-variant/30 rounded-lg p-4">' +
      '<div class="flex items-center gap-2 mb-2"><span class="material-symbols-outlined text-primary icon-fill text-[18px]">auto_awesome</span>' +
      '<h4 class="font-label-lg text-primary">Tại sao phù hợp với bạn</h4></div>' +
      '<p class="font-body-md text-on-surface-variant text-sm">' + escapeHtml(b.why_fit) + '</p>' +
      '</div></div></article>'
    );
  }

  var AI_CACHE_KEY = "ai_recommendations_cache";

  async function initHome() {
    var grid = document.getElementById("recommendations-grid");
    var loading = document.getElementById("recommendations-loading");
    var errEl = document.getElementById("recommendations-error");
    var commentEl = document.getElementById("ai-comment");
    var emptyEl = document.getElementById("recommendations-empty");
    var refreshBtn = document.getElementById("ai-refresh-btn");
    if (!grid) return;

    function showRefreshBtn() {
      if (refreshBtn) refreshBtn.classList.remove("hidden");
    }

    function hideRefreshBtn() {
      if (refreshBtn) refreshBtn.classList.add("hidden");
    }

    function getCurrentTitles() {
      var cached = localStorage.getItem(AI_CACHE_KEY);
      if (!cached) return [];
      try {
        var parsed = JSON.parse(cached);
        return (parsed.recommendations || []).map(function (b) { return b.title; });
      } catch (_) { return []; }
    }

    if (refreshBtn) {
      refreshBtn.addEventListener("click", async function () {
        var currentTitles = getCurrentTitles();
        refreshBtn.disabled = true;
        refreshBtn.innerHTML =
          '<span class="ai-spinner text-primary"></span>' +
          '<span>AI đang tìm đề xuất mới...</span>';
        if (errEl) errEl.classList.add("hidden");
        if (loading) {
          loading.classList.remove("hidden");
          loading.innerHTML = '<div class="flex items-center gap-3"><span class="ai-spinner text-primary"></span><span>AI đang tìm những gợi ý mới cho bạn...</span></div>';
        }
        try {
          var _ref2 = await api.post("/api/ai/recommendations/refresh", { exclude_titles: currentTitles });
          var ok2 = _ref2.ok, data2 = _ref2.data;
          if (!ok2) throw new Error(data2.error || "Không tải được đề xuất mới.");
          // Append new recommendations
          var existing = [];
          var cached = localStorage.getItem(AI_CACHE_KEY);
          if (cached) { try { existing = JSON.parse(cached).recommendations || []; } catch (_) {} }
          var merged = existing.concat(data2.recommendations || []);
          var newCache = { recommendations: merged, comment: data2.comment || (function () { var c = localStorage.getItem(AI_CACHE_KEY); try { return JSON.parse(c).comment || ""; } catch (_) { return ""; } }()) };
          localStorage.setItem(AI_CACHE_KEY, JSON.stringify(newCache));
          // Render new cards appended
          var newHtml = (data2.recommendations || []).map(renderRecommendationCard).join("");
          grid.insertAdjacentHTML("beforeend", newHtml);
          if (commentEl && data2.comment) {
            commentEl.textContent = data2.comment;
            commentEl.parentElement.classList.remove("hidden");
          }
          showRefreshBtn();
        } catch (e) {
          if (e.status === 401) { window.location.href = "login.html"; return; }
          if (errEl) { errEl.textContent = e.message || "Lỗi tải đề xuất mới."; errEl.classList.remove("hidden"); }
          showRefreshBtn();
        } finally {
          if (loading) loading.classList.add("hidden");
          refreshBtn.disabled = false;
          refreshBtn.innerHTML =
            '<span class="material-symbols-outlined text-[18px]" style="font-variation-settings: \'FILL\' 1;">auto_awesome</span>' +
            '<span>Nhận đề xuất khác</span>';
        }
      });
    }

    var needsRefresh = localStorage.getItem("ai_needs_refresh") === "1";

    if (!needsRefresh) {
      var cached = localStorage.getItem(AI_CACHE_KEY);
      if (cached) {
        try {
          var parsed = JSON.parse(cached);
          grid.innerHTML = (parsed.recommendations || []).map(renderRecommendationCard).join("");
          if (commentEl && parsed.comment) {
            commentEl.textContent = parsed.comment;
            commentEl.parentElement.classList.remove("hidden");
          }
          if (loading) loading.classList.add("hidden");
          showRefreshBtn();
          return;
        } catch (_) {}
      }
      // Không có cache và không có flag → hiển thị empty state
      if (loading) loading.classList.add("hidden");
      if (emptyEl) emptyEl.classList.remove("hidden");
      return;
    }

    // Có flag: gọi AI, lưu cache
    localStorage.removeItem("ai_needs_refresh");
    if (emptyEl) emptyEl.classList.add("hidden");
    if (loading) {
      loading.classList.remove("hidden");
      loading.innerHTML = '<div class="flex items-center gap-3"><span class="ai-spinner text-primary"></span><span>AI đang phân tích sở thích của bạn...</span></div>';
    }
    try {
      var _ref = await api.get("/api/ai/recommendations");
      var ok = _ref.ok, data = _ref.data;
      if (!ok) throw new Error(data.error || "Không tải được đề xuất.");
      localStorage.setItem(AI_CACHE_KEY, JSON.stringify(data));
      grid.innerHTML = (data.recommendations || []).map(renderRecommendationCard).join("");
      if (commentEl && data.comment) {
        commentEl.textContent = data.comment;
        commentEl.parentElement.classList.remove("hidden");
      }
      showRefreshBtn();
    } catch (e) {
      if (e.status === 401) { window.location.href = "login.html"; return; }
      if (errEl) { errEl.textContent = e.message || "Lỗi tải đề xuất."; errEl.classList.remove("hidden"); }
    } finally {
      if (loading) loading.classList.add("hidden");
    }
  }

  async function initSurvey() {
    var btn = document.getElementById("survey-submit");
    if (!btn) return;

    // Pre-fill nếu có dữ liệu cũ trong localStorage
    var savedProfile = localStorage.getItem("survey_profile");
    if (savedProfile) {
      try {
        var prof = JSON.parse(savedProfile);
        var ageEl = document.getElementById("age");
        var intEl = document.getElementById("interests");
        var moodEl = document.getElementById("mood");
        if (ageEl && prof.age) ageEl.value = prof.age;
        if (intEl && prof.interests) intEl.value = prof.interests;
        if (moodEl && prof.mood) moodEl.value = prof.mood;
      } catch (_) {}
    }

    btn.addEventListener("click", async function (e) {
      e.preventDefault();
      if (btn.disabled) return;
      btn.disabled = true;
      btn.textContent = "Đang xử lý...";

      var age = document.getElementById("age")?.value;
      var interests = document.getElementById("interests")?.value?.trim() || "";
      var mood = document.getElementById("mood")?.value?.trim() || "";
      var payload = { age: age ? parseInt(age, 10) : null, interests, mood };

      // Lưu profile vào localStorage ngay lập tức
      localStorage.setItem("survey_profile", JSON.stringify(payload));

      try {
        await api.put("/api/user/profile", payload);
      } catch (err) {
        if (err.status === 401) {
          sessionStorage.setItem("pending_profile", JSON.stringify(payload));
          window.location.href = "login.html";
          return;
        }
      }
      sessionStorage.removeItem("pending_profile");
      // Đánh dấu cần gọi AI mới
      localStorage.setItem("ai_needs_refresh", "1");
      window.location.href = "home.html";
    });
  }

  async function applyPendingProfile() {
    const raw = sessionStorage.getItem("pending_profile");
    if (!raw) return;
    try {
      await api.put("/api/user/profile", JSON.parse(raw));
      sessionStorage.removeItem("pending_profile");
    } catch (_) {}
  }

  function missionCardHtml(m) {
    const done = m.completed;
    const pct = m.target_value ? Math.min(100, Math.round((m.current_value / m.target_value) * 100)) : 0;
    const btn = done
      ? '<span class="font-label-sm text-on-surface-variant">Đã nhận</span>'
      : m.timer_minutes
        ? '<button type="button" data-mission-start="' + m.id + '" class="mt-2 font-label-sm text-white bg-primary-container px-3 py-1 rounded-full">Bắt đầu</button>'
        : '<button type="button" data-mission-progress="' + m.id + '" class="mt-2 font-label-sm text-white bg-primary-container px-3 py-1 rounded-full">Tiếp tục</button>';
    return (
      '<div class="bg-white rounded-xl p-md shadow-[0px_4px_20px_rgba(30,41,59,0.05)] border border-[#F1F5F9] flex items-center gap-md relative overflow-hidden">' +
      (done ? "" : '<div class="absolute left-0 top-0 bottom-0 w-1 bg-primary-container"></div>') +
      '<div class="' + (done ? "bg-primary-container/10 text-primary-container" : "bg-surface-container text-on-surface-variant") + ' rounded-full p-3 flex-shrink-0">' +
      '<span class="material-symbols-outlined"' + (done ? ' style="font-variation-settings: \'FILL\' 1;"' : "") + '>' + (m.icon || "menu_book") + '</span></div>' +
      '<div class="flex-grow"><h4 class="font-label-lg ' + (done ? "line-through text-on-surface-variant" : "text-on-surface") + '">' + escapeHtml(m.title) + '</h4>' +
      '<div class="flex justify-between mt-2 mb-1"><span class="font-label-sm text-on-surface-variant">Tiến độ</span><span class="font-label-sm">' + m.current_value + '/' + m.target_value + '</span></div>' +
      '<div class="w-full bg-surface-container-high rounded-full h-2"><div class="bg-primary-container h-2 rounded-full" style="width:' + pct + '%"></div></div></div>' +
      '<div class="flex flex-col items-end flex-shrink-0"><span class="font-label-lg text-primary font-bold">+' + m.xp_reward + ' XP</span>' + btn + '</div></div>'
    );
  }

  function challengeCardHtml(c) {
    const pct = c.target_value ? Math.min(100, Math.round((c.current_value / c.target_value) * 100)) : 0;
    const unit = c.slug === "books-2-month" ? "Cuốn" : c.slug === "hours-10" ? "Phút" : "Ngày";
    const bar = c.slug === "books-2-month" ? "bg-tertiary" : "bg-secondary";
    return (
      '<div class="bg-white rounded-xl p-md shadow border flex flex-col h-full">' +
      '<h4 class="font-headline-md mb-2">' + escapeHtml(c.title) + '</h4>' +
      '<p class="font-body-md text-on-surface-variant mb-4 flex-grow">' + escapeHtml(c.description || "") + '</p>' +
      '<div class="flex justify-between mb-2"><span class="font-label-lg font-bold">' + c.current_value + '/' + c.target_value + ' ' + unit + '</span><span>' + c.xp_reward + ' XP</span></div>' +
      '<div class="w-full bg-surface-container-high rounded-full h-3"><div class="' + bar + ' h-3 rounded-full" style="width:' + pct + '%"></div></div></div>'
    );
  }

  function badgeHtml(b) {
    const locked = !b.unlocked;
    return (
      '<div class="flex flex-col items-center text-center ' + (locked ? "opacity-50 grayscale" : "") + '" title="' + escapeHtml(b.unlock_hint || "") + '">' +
      '<div class="w-16 h-16 rounded-full ' + (locked ? "bg-surface-container" : "bg-primary-fixed border-2 border-primary-container") + ' flex items-center justify-center mb-2">' +
      '<span class="material-symbols-outlined text-3xl ' + (locked ? "text-on-surface-variant" : "text-primary-container") + '">' + b.icon + '</span></div>' +
      '<span class="font-label-sm">' + escapeHtml(b.title) + '</span></div>'
    );
  }

  function bindMissionButtons() {
    document.querySelectorAll("[data-mission-start]").forEach(function (btn) {
      btn.addEventListener("click", async function () {
        const id = btn.getAttribute("data-mission-start");
        const { ok } = await api.post("/api/user/missions/" + id + "/activate", {});
        if (ok) window.location.href = "timer.html";
      });
    });
    document.querySelectorAll("[data-mission-progress]").forEach(function (btn) {
      btn.addEventListener("click", async function () {
        const id = btn.getAttribute("data-mission-progress");
        await api.post("/api/user/missions/" + id + "/progress", { amount: 1 });
        initMissions();
      });
    });
  }

  async function initMissions() {
    const dailyList = document.getElementById("daily-missions-list");
    const challengeGrid = document.getElementById("challenges-grid");
    const badgeGrid = document.getElementById("badges-grid");
    const badgeCount = document.getElementById("badge-count");
    if (!dailyList) return;
    try {
      const { ok, data } = await api.get("/api/user/missions");
      if (!ok) throw new Error(data.error || "Loi");
      const missions = data.missions || [];
      dailyList.innerHTML = missions.map(missionCardHtml).join("");
      if (challengeGrid) challengeGrid.innerHTML = (data.challenges || []).map(challengeCardHtml).join("");
      if (badgeGrid) {
        const badges = data.badges || [];
        if (badgeCount) badgeCount.textContent = badges.filter(function (b) { return b.unlocked; }).length + "/" + badges.length;
        badgeGrid.innerHTML = badges.map(badgeHtml).join("");
      }
      bindMissionButtons();
    } catch (e) {
      if (e.status === 401) window.location.href = "login.html";
    }
  }

  var timerState = { seconds: 0, total: 900, running: false, interval: null };

  function updateTimerUI(display, ring) {
    const s = timerState.seconds;
    const m = Math.floor(s / 60);
    const sec = s % 60;
    if (display) display.textContent = String(m).padStart(2, "0") + ":" + String(sec).padStart(2, "0");
    if (ring) {
      const r = 148;
      const circ = 2 * Math.PI * r;
      ring.setAttribute("stroke-dasharray", String(circ));
      ring.setAttribute("stroke-dashoffset", String(circ * (1 - s / timerState.total)));
    }
  }

  function toggleTimer(display, ring, btn) {
    if (timerState.running) {
      clearInterval(timerState.interval);
      timerState.running = false;
      btn.innerHTML = '<span class="material-symbols-outlined" style="font-variation-settings: \'FILL\' 1;">play_arrow</span> Tiếp tục';
      return;
    }
    timerState.running = true;
    btn.innerHTML = '<span class="material-symbols-outlined" style="font-variation-settings: \'FILL\' 1;">pause</span> Tạm dừng';
    timerState.interval = setInterval(async function () {
      if (timerState.seconds <= 0) {
        clearInterval(timerState.interval);
        timerState.running = false;
        const minutes = Math.ceil(timerState.total / 60);
        try {
          const { ok, data } = await api.post("/api/user/timer/complete", { minutes: minutes });
          if (ok) { alert(data.message || "Hoàn thành!"); window.location.href = "mission.html"; }
          else alert(data.error || "Chưa đủ thời gian.");
        } catch (err) { alert(err.message || "Loi"); }
        return;
      }
      timerState.seconds -= 1;
      updateTimerUI(display, ring);
    }, 1000);
  }

  function resetCancelBtn(el) {
    el.disabled = false;
    el.innerHTML = '<span class="material-symbols-outlined" style="font-variation-settings: \'FILL\' 1;">close</span> Hủy nhiệm vụ';
  }

  async function initTimer() {
    const main = document.getElementById("timer-main");
    const display = document.getElementById("timer-display");
    const btn = document.getElementById("timer-btn");
    const ring = document.getElementById("timer-ring");
    const status = document.getElementById("timer-mission-title");
    const cancelBtn = document.getElementById("timer-cancel-btn");
    if (!main) return;
    try {
      const { ok, data } = await api.get("/api/user/timer/active");
      if (!ok) throw new Error();
      if (!data.active) {
        main.innerHTML = '<div class="text-center px-4 max-w-md"><span class="material-symbols-outlined text-5xl text-primary-container mb-4">info</span><p class="font-headline-md mb-4">Chưa xác định nhiệm vụ</p><p class="font-body-md text-on-surface-variant mb-6">Vui lòng quay lại tab Khám phá để thực hiện nhiệm vụ.</p><a href="mission.html" class="inline-flex bg-primary-container text-on-primary-container px-6 py-3 rounded-full font-label-lg">Đến Khám phá</a></div>';
        return;
      }
      const mins = data.mission.timer_minutes || 15;
      timerState.total = mins * 60;
      timerState.seconds = timerState.total;
      if (status) status.textContent = data.mission.title;
      updateTimerUI(display, ring);
      if (btn) btn.addEventListener("click", function () { toggleTimer(display, ring, btn); });
      if (cancelBtn) {
        cancelBtn.classList.remove("hidden");
        cancelBtn.addEventListener("click", function () {
          document.getElementById("cancel-popup").classList.remove("hidden");
        });
        document.getElementById("cancel-confirm-btn").addEventListener("click", async function () {
          document.getElementById("cancel-popup").classList.add("hidden");
          cancelBtn.disabled = true;
          cancelBtn.innerHTML = '<span class="material-symbols-outlined" style="font-variation-settings: \'FILL\' 1;">sync</span> Đang hủy...';
          if (timerState.running) {
            clearInterval(timerState.interval);
            timerState.running = false;
          }
          try {
            await api.post("/api/user/missions/" + data.mission.id + "/cancel", {});
            window.location.href = "mission.html";
          } catch (_) {
            cancelBtn.disabled = false;
            cancelBtn.innerHTML = '<span class="material-symbols-outlined" style="font-variation-settings: \'FILL\' 1;">close</span> Thất bại';
            setTimeout(function () { resetCancelBtn(cancelBtn); }, 3000);
          }
        });
        document.getElementById("cancel-dismiss-btn").addEventListener("click", function () {
          document.getElementById("cancel-popup").classList.add("hidden");
        });
      }
    } catch (e) {
      if (e.status === 401) window.location.href = "login.html";
    }
  }

  async function initStreak() {
    const streakNum = document.getElementById("streak-count");
    const calendarGrid = document.getElementById("calendar-days");
    const monthLabel = document.getElementById("calendar-month");
    const totalMin = document.getElementById("stat-total-minutes");
    const longest = document.getElementById("stat-longest-streak");
    const books = document.getElementById("stat-books");
    const milestoneBar = document.getElementById("milestone-bar");
    const milestoneText = document.getElementById("milestone-progress");
    if (!streakNum) return;
    const now = new Date();
    var year = now.getFullYear();
    var month = now.getMonth() + 1;
    const names = ["","Tháng 1","Tháng 2","Tháng 3","Tháng 4","Tháng 5","Tháng 6","Tháng 7","Tháng 8","Tháng 9","Tháng 10","Tháng 11","Tháng 12"];
    async function load() {
      const { ok, data } = await api.get("/api/user/streak?year=" + year + "&month=" + month);
      if (!ok) return;
      const st = data.stats;
      streakNum.textContent = st.current_streak;
      if (totalMin) totalMin.innerHTML = st.total_read_minutes + '<span class="font-label-sm ml-1 text-on-surface-variant normal-case">phut</span>';
      if (longest) longest.innerHTML = st.longest_streak + '<span class="font-label-sm ml-1 text-on-surface-variant normal-case">ngay</span>';
      if (books) books.innerHTML = st.books_completed + '<span class="font-label-sm ml-1 text-on-surface-variant normal-case">cuon</span>';
      if (monthLabel) monthLabel.textContent = names[month] + " " + year;
      if (calendarGrid && data.calendar) {
        calendarGrid.innerHTML = data.calendar.days.map(function (d) {
          if (d.read) {
            return '<div class="aspect-square flex flex-col items-center justify-center rounded-full bg-primary-container text-on-primary relative shadow-md"><span class="font-label-lg z-10">' + d.day + '</span><span class="material-symbols-outlined absolute -bottom-1 -right-1 text-[16px]" style="font-variation-settings: \'FILL\' 1;">local_fire_department</span></div>';
          }
          return '<div class="aspect-square flex items-center justify-center rounded-full text-on-surface-variant opacity-50"><span class="font-label-lg">' + d.day + '</span></div>';
        }).join("");
      }
      const ms = data.milestone;
      if (ms && milestoneBar) {
        milestoneBar.style.width = Math.min(100, Math.round((ms.current / ms.target) * 100)) + "%";
        if (milestoneText) milestoneText.textContent = ms.current + "/" + ms.target + " ngay";
      }
    }
    document.getElementById("calendar-prev")?.addEventListener("click", function () {
      month -= 1; if (month < 1) { month = 12; year -= 1; } load();
    });
    document.getElementById("calendar-next")?.addEventListener("click", function () {
      month += 1; if (month > 12) { month = 1; year += 1; } load();
    });
    try { await load(); } catch (e) { if (e.status === 401) window.location.href = "login.html"; }
  }

  document.addEventListener("DOMContentLoaded", function () {
    loadHeaderStreak();
    applyPendingProfile();
    const page = document.body.getAttribute("data-page");
    if (page === "home") initHome();
    if (page === "survey") initSurvey();
    if (page === "mission") initMissions();
    if (page === "timer") initTimer();
    if (page === "streak") initStreak();
  });
})();
