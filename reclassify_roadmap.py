#!/usr/bin/env python3
"""
로드맵 시트 서브프로젝트 재분류 + 부서 재배정
- "펜타-공통" 일괄 → 실제 서브프로젝트
- row 8 (커리큘럼 최종안): 공통 → 펜타스쿨
- row 26 (강사 중계 플랫폼): 펜타캠퍼스 → 펜타웍스
"""
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "1pdW8Xif8ZA75UbkAAbnn02wosNbO5kNnmuJ462E-nqw"
KEY = "/Users/daniel/Downloads/elem-writing-d09737ee13d7.json"

creds = Credentials.from_service_account_file(KEY, scopes=["https://www.googleapis.com/auth/spreadsheets"])
gc = gspread.authorize(creds)
sh = gc.open_by_key(SPREADSHEET_ID)
ws = sh.worksheet("로드맵")

# 로드맵 컬럼: Phase, 마일스톤, 목표일, 상태, 담당, 완료일, 비고, 서브프로젝트, 프로젝트
# (H열=서브프로젝트, I열=프로젝트)

# (sheet_row, new_subproject, new_project_or_None)
# sheet_row은 1-indexed (Python get_all_values 인덱스 + 1)
updates = [
    # 본부
    (3,  "법인 설립", None),        # 대표/지분 구조
    (4,  "브랜드",    None),        # 브랜드명
    (18, "법인 설립", None),        # 법인 형태 결정
    (24, "법인 설립", None),        # 초창패 업종 코드

    # 펜타스쿨
    (6,  "커리큘럼 개발", None),    # 기본 커리큘럼 초안
    (7,  "커리큘럼 개발", None),    # 토요 특강 파일럿
    (8,  "커리큘럼 개발", None),    # 커리큘럼 개발 완료
    (9,  "커리큘럼 개발", "펜타스쿨"),  # 커리큘럼 최종안 — 부서 재배정
    (11, "본점 오픈",     None),    # 본점 오픈 (대치)
    (12, "가맹 확장",     None),    # 2,3호점 오픈
    (13, "가맹 확장",     None),    # 가맹 설명회
    (14, "가맹 확장",     None),    # 10개 지점
    (15, "본점 오픈",     None),    # 입지, 예산
    (19, "커리큘럼 개발", None),    # 심화수업 설계
    (20, "본점 오픈",     None),    # 연구수업

    # 펜타캠퍼스
    (5,  "연수원 구축", None),      # 달콤샘 의사확인
    (10, "연수원 구축", None),      # 강사/원장 풀 안내
    (21, "연수원 구축", None),      # 영역별 담당 대표 강사
    (22, "연수원 구축", None),      # 연수 촬영+편집
    (23, "연수원 구축", None),      # 연수원 (평생교육원 인가)
    (25, "펜타에듀몰",   None),      # 펜타에듀몰 오픈
    (26, "펜타에듀몰",   None),      # 펜타클래스 기획

    # 펜타웍스
    (27, "강사 중계", "펜타웍스"),  # 강사 중계 플랫폼 — 부서 재배정

    # Site-00~07은 이미 "펜타캠퍼스-사이트"
]

# Batch update: H열=서브프로젝트(8), I열=프로젝트(9)
batch = []
for sheet_row, new_sp, new_proj in updates:
    batch.append({"range": f"H{sheet_row}", "values": [[new_sp]]})
    if new_proj:
        batch.append({"range": f"I{sheet_row}", "values": [[new_proj]]})

ws.batch_update(batch, value_input_option="USER_ENTERED")
print(f"✅ {len(updates)}건 업데이트 ({len(batch)} 셀)")

# 결과 확인
from collections import Counter
rows = ws.get_all_values()[2:]
sps = Counter((r[7] if len(r) > 7 else '') for r in rows if any(r))
print("\n서브프로젝트 분포:")
for sp, n in sps.most_common():
    print(f"  {sp or '(공란)'}: {n}")
