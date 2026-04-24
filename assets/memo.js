(function () {
  const GAS_URL = "https://script.google.com/macros/s/AKfycbxN3NaaZpCPPZfH7gEJVOGnyzJp9kvH5KtTXBMh86gnp6OCxcFPN8dGaK7THmVQb9vJoQ/exec";
  const PAGE_NAME = document.title || location.pathname.split("/").pop().replace(".html", "");
  const STORAGE_KEY = "penta_memos_" + location.pathname;

  // ── 섹션 자동 감지 ──────────────────────────────────────────────────────────
  function getSections() {
    const headings = Array.from(document.querySelectorAll("h1, h2, h3, [data-section], section[id]"));
    const seen = new Set();
    const result = [{ id: "__page__", label: "페이지 전체" }];
    headings.forEach((el) => {
      const text = (el.textContent || "").trim().slice(0, 40);
      if (text && !seen.has(text)) {
        seen.add(text);
        result.push({ id: el.id || text, label: text });
      }
    });
    return result;
  }

  // ── 로컬 메모 ────────────────────────────────────────────────────────────────
  function loadMemos() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]"); } catch { return []; }
  }
  function saveMemos(list) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(list)); } catch {}
  }

  // ── CSS ──────────────────────────────────────────────────────────────────────
  const style = document.createElement("style");
  style.textContent = `
    #pm-fab {
      position: fixed; bottom: 28px; right: 28px; z-index: 99999;
      width: 52px; height: 52px; border-radius: 50%;
      background: #C9A84C; color: #fff; border: none;
      font-size: 20px; cursor: pointer;
      box-shadow: 0 4px 16px rgba(0,0,0,0.18);
      display: flex; align-items: center; justify-content: center;
      transition: transform .15s, box-shadow .15s;
    }
    #pm-fab:hover { transform: scale(1.08); box-shadow: 0 6px 20px rgba(0,0,0,0.22); }
    #pm-badge {
      position: absolute; top: -4px; right: -4px;
      background: #0a0a0a; color: #fff;
      font-size: 10px; font-weight: 900; border-radius: 999px;
      min-width: 18px; height: 18px; padding: 0 4px;
      display: flex; align-items: center; justify-content: center;
    }
    #pm-panel {
      position: fixed; bottom: 90px; right: 28px; z-index: 99998;
      width: 340px; max-height: 70vh;
      background: #fff; border-radius: 20px;
      box-shadow: 0 8px 40px rgba(0,0,0,0.16);
      display: flex; flex-direction: column;
      overflow: hidden; opacity: 0; pointer-events: none;
      transform: translateY(12px) scale(0.97);
      transition: opacity .2s, transform .2s;
      font-family: -apple-system, 'Apple SD Gothic Neo', sans-serif;
    }
    #pm-panel.open { opacity: 1; pointer-events: all; transform: none; }
    #pm-header {
      padding: 16px 18px 12px;
      border-bottom: 1px solid #f0f0f0;
      display: flex; align-items: center; justify-content: space-between;
    }
    #pm-header h3 { margin: 0; font-size: 14px; font-weight: 800; color: #0a0a0a; }
    #pm-header span { font-size: 11px; color: #aaa; }
    #pm-close { background: none; border: none; cursor: pointer; font-size: 18px; color: #aaa; padding: 0; }
    #pm-body { padding: 14px 18px; overflow-y: auto; flex: 1; }
    #pm-section-select {
      width: 100%; padding: 9px 12px; border-radius: 10px;
      border: 1.5px solid #e5e5e5; font-size: 13px;
      color: #0a0a0a; background: #fafafa; margin-bottom: 10px;
      outline: none;
    }
    #pm-section-select:focus { border-color: #C9A84C; }
    #pm-textarea {
      width: 100%; box-sizing: border-box; padding: 10px 12px;
      border-radius: 10px; border: 1.5px solid #e5e5e5;
      font-size: 13px; color: #0a0a0a; resize: none;
      font-family: inherit; outline: none; min-height: 80px;
    }
    #pm-textarea:focus { border-color: #C9A84C; }
    #pm-submit {
      width: 100%; margin-top: 10px; padding: 11px;
      background: #0a0a0a; color: #fff; border: none; border-radius: 12px;
      font-size: 13px; font-weight: 700; cursor: pointer;
      transition: background .15s;
    }
    #pm-submit:hover { background: #333; }
    #pm-submit:disabled { opacity: .5; cursor: default; }
    #pm-status { font-size: 11px; color: #C9A84C; margin-top: 6px; min-height: 16px; }
    #pm-list-wrap { margin-top: 14px; }
    #pm-list-title { font-size: 11px; font-weight: 700; color: #aaa; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 8px; }
    .pm-item {
      background: #fafafa; border-radius: 10px; padding: 10px 12px;
      margin-bottom: 8px; border: 1px solid #f0f0f0;
    }
    .pm-item-section { font-size: 10px; font-weight: 700; color: #C9A84C; margin-bottom: 3px; }
    .pm-item-text { font-size: 12px; color: #333; line-height: 1.5; white-space: pre-wrap; }
    .pm-item-date { font-size: 10px; color: #ccc; margin-top: 4px; }
    .pm-item-del { float: right; background: none; border: none; cursor: pointer; font-size: 12px; color: #ddd; }
    .pm-item-del:hover { color: #f44; }
  `;
  document.head.appendChild(style);

  // ── DOM 생성 ─────────────────────────────────────────────────────────────────
  const fab = document.createElement("button");
  fab.id = "pm-fab";
  fab.title = "메모 남기기";
  fab.innerHTML = `✏️<span id="pm-badge" style="display:none"></span>`;
  document.body.appendChild(fab);

  const panel = document.createElement("div");
  panel.id = "pm-panel";
  panel.innerHTML = `
    <div id="pm-header">
      <h3>📝 섹션 메모</h3>
      <span id="pm-page-name"></span>
      <button id="pm-close">✕</button>
    </div>
    <div id="pm-body">
      <select id="pm-section-select"></select>
      <textarea id="pm-textarea" placeholder="이 섹션에 대한 수정 요청이나 메모를 적어주세요"></textarea>
      <button id="pm-submit">메모 저장 + 전송</button>
      <div id="pm-status"></div>
      <div id="pm-list-wrap">
        <div id="pm-list-title">저장된 메모</div>
        <div id="pm-list"></div>
      </div>
    </div>
  `;
  document.body.appendChild(panel);

  // ── 참조 ─────────────────────────────────────────────────────────────────────
  const badge   = document.getElementById("pm-badge");
  const pname   = document.getElementById("pm-page-name");
  const select  = document.getElementById("pm-section-select");
  const textarea= document.getElementById("pm-textarea");
  const submit  = document.getElementById("pm-submit");
  const status  = document.getElementById("pm-status");
  const list    = document.getElementById("pm-list");
  const close   = document.getElementById("pm-close");

  // ── 렌더링 ───────────────────────────────────────────────────────────────────
  function renderList() {
    const memos = loadMemos();
    badge.textContent = memos.length;
    badge.style.display = memos.length ? "flex" : "none";
    list.innerHTML = memos.length === 0
      ? `<p style="font-size:12px;color:#ccc;text-align:center;margin:8px 0">아직 메모가 없습니다</p>`
      : memos.map((m, i) => `
          <div class="pm-item">
            <button class="pm-item-del" data-i="${i}">✕</button>
            <div class="pm-item-section">${m.section}</div>
            <div class="pm-item-text">${m.text}</div>
            <div class="pm-item-date">${m.date}</div>
          </div>`).join("");

    list.querySelectorAll(".pm-item-del").forEach((btn) => {
      btn.addEventListener("click", () => {
        const memos = loadMemos();
        memos.splice(Number(btn.dataset.i), 1);
        saveMemos(memos);
        renderList();
      });
    });
  }

  function populateSections() {
    getSections().forEach((s) => {
      const opt = document.createElement("option");
      opt.value = s.id;
      opt.textContent = s.label;
      select.appendChild(opt);
    });
  }

  function openPanel() {
    pname.textContent = PAGE_NAME.slice(0, 20);
    if (!select.options.length) populateSections();
    renderList();
    panel.classList.add("open");
  }

  // ── 이벤트 ───────────────────────────────────────────────────────────────────
  fab.addEventListener("click", () => {
    panel.classList.contains("open") ? panel.classList.remove("open") : openPanel();
  });
  close.addEventListener("click", () => panel.classList.remove("open"));

  submit.addEventListener("click", async () => {
    const text = textarea.value.trim();
    if (!text) { status.textContent = "메모 내용을 입력해주세요."; return; }
    const section = select.options[select.selectedIndex]?.text || "전체";
    const date = new Date().toLocaleString("ko-KR");

    // 로컬 저장
    const memos = loadMemos();
    memos.unshift({ section, text, date });
    saveMemos(memos);

    // GAS → 수정요청 시트 전송
    submit.disabled = true;
    status.textContent = "전송 중...";
    try {
      const payload = JSON.stringify({
        action: "append", sheet: "수정요청",
        values: [date, "[" + PAGE_NAME + "] " + section, "메모", text, "", location.href],
      });
      await fetch(`${GAS_URL}?payload=${encodeURIComponent(payload)}`, { method: "GET", mode: "no-cors" });
      status.textContent = "✓ 저장 완료 — 이은경 대표에게 알림 전송됨";
    } catch {
      status.textContent = "⚠ 로컬 저장만 됨 (전송 실패)";
    }
    textarea.value = "";
    submit.disabled = false;
    renderList();
    setTimeout(() => { status.textContent = ""; }, 3000);
  });

  // 패널 외부 클릭 시 닫기
  document.addEventListener("click", (e) => {
    if (!panel.contains(e.target) && e.target !== fab) {
      panel.classList.remove("open");
    }
  });

  // 초기 뱃지
  renderList();
})();
