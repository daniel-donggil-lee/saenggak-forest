#!/usr/bin/env python3
"""
펜타 보드 생애주기 시트 통합 마이그레이션
아이디어 / 조사 / 의사결정 / 합의사항 → 논의 (단일 시트, 상태 컬럼)

실행: python3 migrate_to_논의.py
"""
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

SPREADSHEET_ID = "1pdW8Xif8ZA75UbkAAbnn02wosNbO5kNnmuJ462E-nqw"
KEY = "/Users/daniel/Downloads/elem-writing-d09737ee13d7.json"
TODAY = date.today().isoformat()
HIST = f"{TODAY} 마이그레이션"

creds = Credentials.from_service_account_file(
    KEY,
    scopes=["https://www.googleapis.com/auth/spreadsheets"],
)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SPREADSHEET_ID)


def merge(*parts):
    return "\n\n".join(p for p in parts if p and p.strip())


def row(cat, title, content, status, owner="", proj="", sub="", prio="",
        choices="", rationale="", report=""):
    """논의 시트 14컬럼 구조로 행 생성."""
    return [
        cat or "", title or "", content or "", status,
        owner or "", proj or "", sub or "", prio or "",
        choices or "", rationale or "", report or "",
        TODAY, TODAY, HIST,
    ]


records = []

# ============================================================
# 1. 아이디어 시트 → 상태=아이디어
# ============================================================
ideas = sh.worksheet("아이디어").get_all_values()
for r in ideas[2:]:
    if not any(r) or not (r[1] if len(r) > 1 else ""):
        continue
    cat, title, content, src, method, note = (r + [""] * 8)[:6]
    proj = r[6] if len(r) > 6 else ""
    sub = r[7] if len(r) > 7 else ""
    records.append(row(
        cat, title, content, "아이디어",
        owner=src, proj=proj, sub=sub,
        rationale=merge(method, note),
    ))

# ============================================================
# 2. 조사 시트 → 대기/진행중=조사중, 완료=결정대기
# ============================================================
res = sh.worksheet("조사").get_all_values()
for r in res[2:]:
    if not any(r):
        continue
    # divider/header rows
    first = (r[0] or "").strip()
    if first.startswith("✓") or first == "":
        if not (r[1] if len(r) > 1 else "").strip():
            continue
    cat, title, purpose, state, summary, note = (r + [""] * 9)[:6]
    report = r[6] if len(r) > 6 else ""
    proj = r[7] if len(r) > 7 else ""
    sub = r[8] if len(r) > 8 else ""
    if not title.strip():
        continue
    status = "결정대기" if state.strip() == "완료" else "조사중"
    records.append(row(
        cat, title, purpose, status,
        proj=proj, sub=sub,
        rationale=merge(summary, note),
        report=report,
    ))

# ============================================================
# 3. 의사결정 시트 → 비고에 "✅" 또는 "확정" 있으면 합의(중복 스킵 후보), 그 외 우선순위 기반
# ============================================================
dec = sh.worksheet("의사결정").get_all_values()
# 합의사항과 중복되는 제목 (수동 식별)
DEDUP_TITLES = {"대표자 / 지분 설정", "브랜드명", "펜타 사업 범위 확정"}
for r in dec[2:]:
    if not any(r):
        continue
    cat, title, prio, choices, basis, owner, note = (r + [""] * 9)[:7]
    proj = r[7] if len(r) > 7 else ""
    sub = r[8] if len(r) > 8 else ""
    if not title.strip():
        continue
    if title.strip() in DEDUP_TITLES:
        # 합의사항에 최종 버전 있음 → 스킵
        continue
    # 상태 판정 (✅ 마커만 확정 신호로 인정. "확정" 문자열은 다른 맥락에서도 쓰임)
    if "✅" in note:
        status = "합의"
    elif prio.strip() == "보류":
        status = "보류"
    else:
        status = "결정대기"
    records.append(row(
        cat, title, "", status,
        owner=owner, proj=proj, sub=sub,
        prio=prio if prio.strip() not in ("", "보류") else "",
        choices=choices, rationale=merge(basis, note),
    ))

# ============================================================
# 4. 합의사항 시트 → 상태=합의
# ============================================================
agr = sh.worksheet("합의사항").get_all_values()
# 헤더성 행 (내용 없이 "역할: ..."만 있는 것들)
HEADER_LIKE = {"역할: 이은경", "역할: 이동길"}
for r in agr[2:]:
    if not any(r):
        continue
    cat, title, content, owner, note = (r + [""] * 7)[:5]
    proj = r[5] if len(r) > 5 else ""
    sub = r[6] if len(r) > 6 else ""
    title_s = title.strip()
    if not title_s:
        continue
    if title_s in HEADER_LIKE:
        continue
    records.append(row(
        cat, title, content, "합의",
        owner=owner, proj=proj, sub=sub,
        rationale=note,
    ))

# ============================================================
# 쓰기
# ============================================================
ws = sh.worksheet("논의")
start_row = 3  # 1=제목, 2=헤더
end_row = start_row + len(records) - 1
rng = f"A{start_row}:N{end_row}"
ws.update(rng, records, value_input_option="USER_ENTERED")

print(f"✅ 마이그레이션 완료: {len(records)}건 → 논의!{rng}")
# 상태별 카운트
from collections import Counter
cnt = Counter(r[3] for r in records)
for s in ["아이디어", "조사중", "결정대기", "합의", "보류", "폐기"]:
    print(f"  {s}: {cnt.get(s, 0)}건")
