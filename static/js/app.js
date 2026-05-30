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
    var commentSection = commentEl ? commentEl.parentElement : null;
    var emptyEl = document.getElementById("recommendations-empty");
    var refreshBtn = document.getElementById("ai-refresh-btn");
    var clearBtn = document.getElementById("ai-clear-btn");
    if (!grid) return;

    function showRefreshBtn() {
      if (refreshBtn) refreshBtn.classList.remove("hidden");
    }
    function hideRefreshBtn() {
      if (refreshBtn) refreshBtn.classList.add("hidden");
    }
    function showClearBtn() {
      if (clearBtn) clearBtn.classList.remove("hidden");
    }
    function hideClearBtn() {
      if (clearBtn) clearBtn.classList.add("hidden");
    }
    function showEmptyState() {
      if (emptyEl) emptyEl.classList.remove("hidden");
      hideRefreshBtn();
      hideClearBtn();
    }
    function hideEmptyState() {
      if (emptyEl) emptyEl.classList.add("hidden");
    }
    function showComment(text) {
      if (commentEl && text) {
        commentEl.textContent = text;
        if (commentSection) commentSection.classList.remove("hidden");
      } else {
        if (commentEl) commentEl.textContent = "";
        if (commentSection) commentSection.classList.add("hidden");
      }
    }
    function hasValidCache() {
      var cached = localStorage.getItem(AI_CACHE_KEY);
      if (!cached) return false;
      try {
        var parsed = JSON.parse(cached);
        var recs = parsed.recommendations || [];
        return recs.length > 0;
      } catch (_) { return false; }
    }

    function getCurrentTitles() {
      var cached = localStorage.getItem(AI_CACHE_KEY);
      if (!cached) return [];
      try {
        var parsed = JSON.parse(cached);
        return (parsed.recommendations || []).map(function (b) { return b.title; });
      } catch (_) { return []; }
    }

    function clearRecommendations() {
      localStorage.removeItem(AI_CACHE_KEY);
      grid.innerHTML = "";
      showComment("");
      showEmptyState();
    }

    function renderFromCache() {
      var cached = localStorage.getItem(AI_CACHE_KEY);
      if (!cached) return false;
      try {
        var parsed = JSON.parse(cached);
        var recs = parsed.recommendations || [];
        if (recs.length === 0) return false;
        grid.innerHTML = recs.map(renderRecommendationCard).join("");
        showComment(parsed.comment);
        hideEmptyState();
        showRefreshBtn();
        showClearBtn();
        return true;
      } catch (_) { return false; }
    }

    var deletePopup = document.getElementById("delete-popup");
    var deleteConfirmBtn = document.getElementById("delete-confirm-btn");
    var deleteDismissBtn = document.getElementById("delete-dismiss-btn");

    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        if (deletePopup) deletePopup.classList.remove("hidden");
      });
    }
    if (deleteConfirmBtn) {
      deleteConfirmBtn.addEventListener("click", function () {
        clearRecommendations();
        if (deletePopup) deletePopup.classList.add("hidden");
      });
    }
    if (deleteDismissBtn) {
      deleteDismissBtn.addEventListener("click", function () {
        if (deletePopup) deletePopup.classList.add("hidden");
      });
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
          var existing = [];
          var cached = localStorage.getItem(AI_CACHE_KEY);
          if (cached) { try { existing = JSON.parse(cached).recommendations || []; } catch (_) {} }
          var merged = existing.concat(data2.recommendations || []);
          var newCache = { recommendations: merged, comment: data2.comment || (function () { var c = localStorage.getItem(AI_CACHE_KEY); try { return JSON.parse(c).comment || ""; } catch (_) { return ""; } }()) };
          localStorage.setItem(AI_CACHE_KEY, JSON.stringify(newCache));
          var newHtml = (data2.recommendations || []).map(renderRecommendationCard).join("");
          grid.insertAdjacentHTML("beforeend", newHtml);
          if (commentEl && data2.comment) {
            commentEl.textContent = data2.comment;
            if (commentSection) commentSection.classList.remove("hidden");
          }
          hideEmptyState();
          showRefreshBtn();
          showClearBtn();
        } catch (e) {
          if (e.status === 401) { window.location.href = "login.html"; return; }
          if (errEl) { errEl.textContent = e.message || "Lỗi tải đề xuất mới."; errEl.classList.remove("hidden"); }
          showRefreshBtn();
          if (hasValidCache()) showClearBtn();
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
      if (renderFromCache()) return;
      if (loading) loading.classList.add("hidden");
      showEmptyState();
      return;
    }

    localStorage.removeItem("ai_needs_refresh");
    hideEmptyState();
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
      showComment(data.comment);
      hideEmptyState();
      showRefreshBtn();
      showClearBtn();
    } catch (e) {
      if (e.status === 401) { window.location.href = "login.html"; return; }
      if (!renderFromCache()) {
        showEmptyState();
      }
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

  var timerState = { seconds: 0, total: 900, running: false, interval: null, startedAt: null, completed: false };

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
      timerState.startedAt = null;
      btn.innerHTML = '<span class="material-symbols-outlined" style="font-variation-settings: \'FILL\' 1;">play_arrow</span> Tiếp tục';
      return;
    }
    timerState.running = true;
    if (!timerState.startedAt) timerState.startedAt = Date.now();
    btn.innerHTML = '<span class="material-symbols-outlined" style="font-variation-settings: \'FILL\' 1;">pause</span> Tạm dừng';
    timerState.interval = setInterval(async function () {
      var elapsed = Math.floor((Date.now() - timerState.startedAt) / 1000);
      var remaining = timerState.total - elapsed;
      timerState.seconds = Math.max(0, remaining);
      updateTimerUI(display, ring);
      if (timerState.seconds <= 0) {
        clearInterval(timerState.interval);
        timerState.running = false;
        timerState.completed = true;
        document.getElementById("journal-popup")?.classList.remove("hidden");
      }
    }, 200);
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

      var journalInput = document.getElementById("journal-input");
      var journalWordCount = document.getElementById("journal-word-count");
      var journalWordError = document.getElementById("journal-word-error");
      var journalSubmitBtn = document.getElementById("journal-submit-btn");
      var journalSkipBtn = document.getElementById("journal-skip-btn");

      if (journalInput && journalWordCount) {
        journalInput.addEventListener("input", function () {
          var text = journalInput.value.trim();
          var words = text ? text.split(/\s+/).length : 0;
          journalWordCount.textContent = words + " / 30 tu";
          if (words >= 30) {
            journalSubmitBtn.disabled = false;
            journalSubmitBtn.className = "w-full bg-primary-container text-on-primary-container font-label-lg py-3 rounded-full hover:bg-primary transition-all active:scale-95";
            if (journalWordError) journalWordError.classList.add("hidden");
          } else {
            journalSubmitBtn.disabled = true;
            journalSubmitBtn.className = "w-full bg-surface-container-high text-on-surface-variant font-label-lg py-3 rounded-full cursor-not-allowed";
          }
        });
      }

      if (journalSubmitBtn) {
        journalSubmitBtn.addEventListener("click", async function () {
          var text = journalInput ? journalInput.value.trim() : "";
          var words = text ? text.split(/\s+/).length : 0;
          if (words < 30) {
            if (journalWordError) journalWordError.classList.remove("hidden");
            return;
          }
          journalSubmitBtn.disabled = true;
          journalSubmitBtn.textContent = "Dang xu ly...";
          var minutes = Math.ceil(timerState.total / 60);
          try {
            var _res = await api.post("/api/user/timer/complete", { minutes: minutes, journal: text });
            if (_res.ok) {
              document.getElementById("journal-popup")?.classList.add("hidden");
              window.location.href = "mission.html";
            } else {
              alert(_res.data.error || "Loi");
              journalSubmitBtn.disabled = false;
              journalSubmitBtn.textContent = "Xac nhan";
            }
          } catch (err) {
            alert(err.message || "Loi");
            journalSubmitBtn.disabled = false;
            journalSubmitBtn.textContent = "Xac nhan";
          }
        });
      }

      if (journalSkipBtn) {
        journalSkipBtn.addEventListener("click", function () {
          document.getElementById("journal-popup")?.classList.add("hidden");
          window.location.href = "mission.html";
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

  async function initLeaderboard() {
    var list = document.getElementById("leaderboard-list");
    var loading = document.getElementById("leaderboard-loading");
    var errEl = document.getElementById("leaderboard-error");
    var emptyEl = document.getElementById("leaderboard-empty");
    var podium = document.getElementById("podium-section");
    if (!list) return;
    try {
      var _r = await api.get("/api/user/leaderboard");
      if (!_r.ok) throw new Error(_r.data.error || "Loi");
      var entries = _r.data.leaderboard || [];
      if (loading) loading.classList.add("hidden");
      if (entries.length === 0) {
        if (emptyEl) emptyEl.classList.remove("hidden");
        return;
      }
      var top3 = entries.slice(0, 3);
      var medals = ["emoji_events", "military_tech", "workspace_premium"];
      var medalColors = ["text-amber-400", "text-slate-400", "text-amber-700"];
      var bgColors = ["bg-amber-50 border-amber-200", "bg-slate-50 border-slate-200", "bg-orange-50 border-orange-200"];
      if (podium) {
        podium.classList.remove("hidden");
        podium.querySelector("div").innerHTML = top3.map(function (e, i) {
          var h = i === 0 ? "h-32" : i === 1 ? "h-24" : "h-20";
          return '<div class="flex flex-col items-center gap-2 w-1/3"><div class="' + medalColors[i] + '"><span class="material-symbols-outlined text-4xl" style="font-variation-settings: \'FILL\' 1;">' + medals[i] + '</span></div><div class="w-14 h-14 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-headline-md text-headline-md shadow-md border-2 border-white">' + e.initials + '</div><p class="font-label-sm text-center text-on-surface leading-tight mt-1">' + escapeHtml(e.full_name) + '</p><p class="font-label-lg text-primary-container font-bold">' + e.current_streak + ' ngày</p></div>';
        }).join("");
      }
      list.classList.remove("hidden");
      list.innerHTML = entries.map(function (e, i) {
        var rankClass = i < 3 ? medalColors[i] + " font-bold" : "text-on-surface-variant";
        var rankBg = i < 3 ? "bg-primary-container/10" : "";
        return '<div class="flex items-center gap-3 bg-surface-container-lowest rounded-xl p-3 md:p-4 shadow-sm border border-outline-variant/30 hover:shadow-md transition-shadow"><div class="flex-shrink-0 w-8 text-center font-label-lg ' + rankClass + '">#' + e.rank + '</div><div class="w-10 h-10 rounded-full bg-primary-container/20 text-primary-container flex items-center justify-center font-label-sm font-bold text-sm">' + e.initials + '</div><div class="flex-grow min-w-0"><p class="font-label-sm text-on-surface truncate">' + escapeHtml(e.full_name) + '</p><div class="flex gap-3 text-xs text-on-surface-variant mt-1"><span>🔥 ' + e.current_streak + ' ngày</span><span>⏱ ' + e.total_read_minutes + ' phút</span><span>⭐ ' + e.xp + ' XP</span></div></div></div>';
      }).join("");
    } catch (e) {
      if (loading) loading.classList.add("hidden");
      if (e.status === 401) { if (emptyEl) emptyEl.classList.remove("hidden"); return; }
      if (errEl) { errEl.textContent = e.message || "Không thể tải bảng xếp hạng."; errEl.classList.remove("hidden"); }
    }
  }

  function bookCardHtml(b) {
    var cat = b.category || {};
    return (
      '<div class="bg-surface-container-lowest rounded-xl overflow-hidden shadow-sm border border-outline-variant/30 hover:shadow-md transition-shadow cursor-pointer" data-book-id="' + b.id + '">' +
      '<div class="p-6">' +
      '<div class="flex items-center gap-2 mb-3">' +
      '<span class="material-symbols-outlined text-primary-container text-[18px]">' + (cat.icon || "book") + '</span>' +
      '<span class="font-label-sm text-on-surface-variant bg-surface-container px-2 py-0.5 rounded-full">' + escapeHtml(cat.title || "Khác") + '</span>' +
      '</div>' +
      '<h3 class="font-headline-md text-on-surface mb-2">' + escapeHtml(b.title) + '</h3>' +
      '<p class="font-body-md text-on-surface-variant line-clamp-3 text-sm">' + escapeHtml(b.description || "") + '</p>' +
      '</div>' +
      '</div>'
    );
  }

  function sectionCardHtml(slug, title, icon, books) {
    return (
      '<section class="space-y-sm">' +
      '<div class="flex items-center gap-2 mb-1">' +
      '<span class="material-symbols-outlined text-primary-container text-[22px]">' + icon + '</span>' +
      '<h3 class="font-headline-md text-on-surface">' + escapeHtml(title) + '</h3>' +
      '<span class="font-label-sm text-on-surface-variant">(' + books.length + ')</span>' +
      '</div>' +
      '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-sm">' +
      books.map(bookCardHtml).join("") +
      '</div></section>'
    );
  }

  async function initLibrary() {
    var container = document.getElementById("books-container");
    var loading = document.getElementById("library-loading");
    var errEl = document.getElementById("library-error");
    var emptyEl = document.getElementById("library-empty");
    var searchInput = document.getElementById("library-search");
    var pillsEl = document.getElementById("category-pills");
    var popup = document.getElementById("book-popup");
    var popupTitle = document.getElementById("popup-title");
    var popupCategory = document.getElementById("popup-category");
    var popupCategoryIcon = document.getElementById("popup-category-icon");
    var popupContent = document.getElementById("popup-content");
    var popupClose = document.getElementById("popup-close");
    var commentsList = document.getElementById("comments-list");
    var commentsLoading = document.getElementById("comments-loading");
    var commentCount = document.getElementById("comment-count");
    var commentInput = document.getElementById("comment-input");
    var commentSubmit = document.getElementById("comment-submit");
    var commentError = document.getElementById("comment-error");
    var commentLoginPrompt = document.getElementById("comment-login-prompt");
    if (!container) return;

    var allBooks = [];
    var selectedCategory = "";

    function escapeHtmlContent(s) {
      var d = document.createElement("div");
      d.textContent = s || "";
      return d.innerHTML;
    }

    function render() {
      var q = searchInput ? searchInput.value.toLowerCase().trim() : "";
      var filtered = allBooks.filter(function (b) {
        if (selectedCategory && b.category.slug !== selectedCategory) return false;
        if (q && b.title.toLowerCase().indexOf(q) === -1 && (b.description || "").toLowerCase().indexOf(q) === -1) return false;
        return true;
      });

      if (filtered.length === 0) {
        container.innerHTML = "";
        if (emptyEl) emptyEl.classList.remove("hidden");
        return;
      }
      if (emptyEl) emptyEl.classList.add("hidden");

      var cats = {};
      filtered.forEach(function (b) {
        var s = b.category.slug || "khac";
        if (!cats[s]) cats[s] = { title: b.category.title || "Khác", icon: b.category.icon || "book", books: [] };
        cats[s].books.push(b);
      });

      var catOrder = ["van-hoc", "kinh-te", "phat-trien", "khoa-hoc", "cong-nghe", "marketing", "ngon-ngu", "nghe-thuat", "truyen-tranh", "hoi-ky", "khac"];
      var html = "";
      catOrder.forEach(function (s) {
        if (cats[s]) {
          html += sectionCardHtml(s, cats[s].title, cats[s].icon, cats[s].books);
        }
      });
      container.innerHTML = html;

      container.querySelectorAll("[data-book-id]").forEach(function (el) {
        el.addEventListener("click", function () {
          var id = parseInt(el.getAttribute("data-book-id"), 10);
          openBookDetail(id);
        });
      });
    }

    var currentBookId = null;

    function renderComment(c) {
      var initials = (c.user_name || "?").split(" ").map(function (w) { return w[0]; }).join("").toUpperCase().slice(0, 2);
      var timeAgo = "";
      if (c.created_at) {
        var d = new Date(c.created_at);
        var now = new Date();
        var diff = Math.floor((now - d) / 1000);
        if (diff < 60) timeAgo = "Vừa xong";
        else if (diff < 3600) timeAgo = Math.floor(diff / 60) + " phút trước";
        else if (diff < 86400) timeAgo = Math.floor(diff / 3600) + " giờ trước";
        else if (diff < 2592000) timeAgo = Math.floor(diff / 86400) + " ngày trước";
        else timeAgo = d.toLocaleDateString("vi-VN");
      }
      return (
        '<div class="flex gap-3 p-3 bg-surface-container-low rounded-xl">' +
        '<div class="w-8 h-8 rounded-full bg-primary-container/20 text-primary-container flex items-center justify-center font-label-sm font-bold text-sm flex-shrink-0">' + initials + '</div>' +
        '<div class="flex-1 min-w-0">' +
        '<div class="flex items-center gap-2 mb-1">' +
        '<span class="font-label-sm font-semibold text-on-surface">' + escapeHtml(c.user_name) + '</span>' +
        '<span class="font-label-sm text-on-surface-variant text-xs">' + timeAgo + '</span>' +
        '</div>' +
        '<p class="font-body-md text-on-surface-variant text-sm">' + escapeHtml(c.content) + '</p>' +
        '</div></div>'
      );
    }

    async function loadComments(bookId) {
      if (!commentsList || !commentsLoading) return;
      commentsLoading.classList.remove("hidden");
      commentsList.innerHTML = "";
      try {
        var _r = await api.get("/api/library/" + bookId + "/comments");
        if (_r.ok) {
          var cmts = _r.data.comments || [];
          if (commentCount) commentCount.textContent = "(" + cmts.length + ")";
          if (cmts.length === 0) {
            commentsList.innerHTML = '<p class="font-body-md text-on-surface-variant text-sm py-2 text-center">Chưa có bình luận nào. Hãy là người đầu tiên!</p>';
          } else {
            commentsList.innerHTML = cmts.map(renderComment).join("");
          }
        }
      } catch (e) {}
      commentsLoading.classList.add("hidden");
    }

    async function openBookDetail(id) {
      currentBookId = id;
      if (!popup) return;
      popupTitle.textContent = "Đang tải...";
      popupContent.textContent = "";
      popup.classList.remove("hidden");
      if (commentsList) commentsList.innerHTML = "";
      if (commentCount) commentCount.textContent = "(0)";
      if (commentError) commentError.classList.add("hidden");
      if (commentInput) commentInput.value = "";
      if (commentSubmit) commentSubmit.disabled = true;
      try {
        var _ref = await api.get("/api/library/" + id);
        if (!_ref.ok) throw new Error(_ref.data.error || "Lỗi");
        var book = _ref.data.book;
        var content = _ref.data.content || "";
        popupTitle.textContent = book.title;
        if (popupCategory) popupCategory.textContent = book.category.title;
        if (popupCategoryIcon) popupCategoryIcon.textContent = book.category.icon || "book";
        popupContent.textContent = content;
        loadComments(id);
      } catch (e) {
        popupContent.textContent = e.message || "Không thể tải nội dung sách.";
      }
    }

    if (popupClose) {
      popupClose.addEventListener("click", function () {
        popup.classList.add("hidden");
      });
      popup.addEventListener("click", function (e) {
        if (e.target === popup) popup.classList.add("hidden");
      });
    }

    if (commentInput && commentSubmit) {
      commentInput.addEventListener("input", function () {
        var val = commentInput.value.trim();
        commentSubmit.disabled = val.length === 0 || val.length > 1000;
      });
      commentSubmit.addEventListener("click", async function () {
        if (!currentBookId || !commentInput) return;
        var val = commentInput.value.trim();
        if (!val || val.length > 1000) return;
        commentSubmit.disabled = true;
        if (commentError) commentError.classList.add("hidden");
        try {
          var _res = await api.post("/api/library/" + currentBookId + "/comments", { content: val });
          if (!_res.ok) {
            if (commentError) {
              commentError.textContent = _res.data.error || "Không thể gửi bình luận.";
              commentError.classList.remove("hidden");
            }
            commentSubmit.disabled = false;
            return;
          }
          commentInput.value = "";
          commentSubmit.disabled = true;
          loadComments(currentBookId);
        } catch (e) {
          if (e.status === 401) {
            window.location.href = "login.html";
            return;
          }
          if (commentError) {
            commentError.textContent = e.message || "Lỗi kết nối.";
            commentError.classList.remove("hidden");
          }
          commentSubmit.disabled = false;
        }
      });
    }

    if (commentLoginPrompt) {
      try {
        var _ck = await api.get("/api/user/stats");
        if (_ck.ok) commentLoginPrompt.classList.add("hidden");
      } catch (e) {
        commentLoginPrompt.classList.remove("hidden");
        if (commentInput) commentInput.disabled = true;
        if (commentSubmit) commentSubmit.disabled = true;
      }
    }

    if (searchInput) {
      searchInput.addEventListener("input", function () { render(); });
    }

    function renderPills(categories) {
      if (!pillsEl) return;
      var html = '<button data-cat="" class="pill px-4 py-1.5 rounded-full font-label-sm transition-colors ' + (selectedCategory === "" ? "bg-primary text-on-primary" : "bg-surface-container text-on-surface-variant hover:bg-surface-container-high") + '">Tất cả</button>';
      categories.forEach(function (c) {
        var active = selectedCategory === c.slug;
        html += '<button data-cat="' + c.slug + '" class="pill px-4 py-1.5 rounded-full font-label-sm transition-colors flex items-center gap-1.5 whitespace-nowrap ' + (active ? "bg-primary text-on-primary" : "bg-surface-container text-on-surface-variant hover:bg-surface-container-high") + '">' +
          '<span class="material-symbols-outlined text-[16px]">' + c.icon + '</span>' +
          c.title +
        '</button>';
      });
      pillsEl.innerHTML = html;
      pillsEl.querySelectorAll("[data-cat]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          selectedCategory = btn.getAttribute("data-cat");
          renderPills(categories);
          render();
        });
      });
    }

    try {
      var _res = await api.get("/api/library");
      if (!_res.ok) throw new Error(_res.data.error || "Lỗi");
      allBooks = _res.data.books || [];
      if (loading) loading.classList.add("hidden");
      if (allBooks.length === 0) {
        if (emptyEl) emptyEl.classList.remove("hidden");
        return;
      }
      var _res2 = await api.get("/api/library/categories");
      var categories = _res2.ok ? (_res2.data.categories || []) : [];
      renderPills(categories);
      render();
    } catch (e) {
      if (loading) loading.classList.add("hidden");
      if (errEl) {
        errEl.textContent = e.message || "Không thể tải thư viện.";
        errEl.classList.remove("hidden");
      }
    }
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
    if (page === "leaderboard") initLeaderboard();
    if (page === "library") initLibrary();
  });
})();
