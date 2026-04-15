# 펜타보드 대시보드 단순화 — 작업 노트

> 세션 일자: 2026-04-15
> 다음 세션에서 이어갈 수 있도록 맥락·결정·미완 항목 상세 기록

---

## 1. 문제 인식 (왜 단순화하는가)

### 사용자 발화 (원문)
- "각 부서별로 이 구조를 그대로 두는게 맞을까??"
- "근데 이미 로드맵 할일 아이디어 의사결정 합의사항 같은것들이 모든 부서에 해당해야 하는지도 의문"
- "더 단순화했으면 좋겠어"
- "내가 실제로 처리하거나 보지 않을 정도로 많은 일들이 할일 목록에 들어가는 문제가 생기는것 같아"

### 진단
- **기존 10개 탭 구조**가 부서별로 반복 → 인지 부하 과다
- 부서 성숙도와 무관하게 모든 탭을 다 가진 구조 → 빈 탭·죽은 탭 많음
- 할일 시트가 진짜 "이번 주 할 것"과 "언젠가 할 것"이 뒤섞여 부풀어오름
- Daniel이 실제로 안 보게 되는 임계치 = 시스템 실패 포인트

---

## 2. 이번 세션에서 결정·구현 완료된 것

### 2-1. 탭 체계 3+2로 압축

**기능 탭 (부서별 뷰, 부서 필터 적용됨):**
```javascript
FUNCTIONAL_TABS = ['할일', '로드맵', '기록']
```

**광역 탭 (전 부서 통합, 필터 없음):**
```javascript
GLOBAL_TABS = ['공지사항', '리포트']
```

**기록 탭의 내부 구성:**
```javascript
ARCHIVE_SOURCES = ['아이디어', '조사', '의사결정', '합의사항', '회의록']
```
→ 5개 원본 시트를 통합 뷰로 표시. 사용자에겐 "기록" 1개로 보임.

### 2-2. 기록 탭 (renderArchivePanel) 구현

- **chip 필터**: 전체 / 아이디어 / 조사 / 결정 / 합의 / 회의록
  - 각 chip에 카운트 표시: `아이디어<b>3</b>`
  - 활성 chip은 해당 소스 색으로 배경 채움
- **카드 리스트**: 소스별 색상 태그 (보라=아이디어, 파랑=조사, 골드=결정, 초록=합의, 회색=회의록)
- **카드 클릭** → 원본 시트의 `openEditModal(src, rowIdx)` 호출 → 기존 편집 모달 재사용
- **SOURCE_META**: 색상·태그명 매핑 객체 (renderArchivePanel 내부)
- **부서 필터 호환**: 각 소스에서 프로젝트 컬럼 확인 후 currentDept 일치 항목만

### 2-3. 할일 탭 상단 2개 섹션 추가

**(A) 📎 산출물 링크 카드 그리드 (renderDeliverables)**
- 로드맵 시트의 `비고` 열에서 URL 정규식(`https?:\/\/[^\s]+`) 자동 추출
- 마일스톤·목표일·상태·프로젝트와 함께 카드로 렌더링
- 상태별 색상: 완료=초록+흐림, 진행중=골드, 대기=회색
- **현재 시트 상태**: Site-00~03 (Discovery/PRD/IA/Mockup) 4개 URL 입력 완료
  - service account(elem-writing-d09737ee13d7.json)로 G30~G33 업데이트했음

**(B) 💬 최근 피드백 피드 (fetchFeedback)**
- DanielFlow Comment 광역 엔드포인트 호출
- 프로젝트 무관 최신 5건 표시 (프로젝트 배지·작성자·평점·타임스탬프·코멘트)
- 엔드포인트: `https://script.google.com/macros/s/AKfycbyGbLdZSuRfvWC-Yy9xEh9AbIX7NMPWr4EW4cXnP3BPC22AHAtJKI-fixY5W7dk14Kw/exec`

### 2-4. CSS 추가 완료

- `.archive-chips`, `.archive-chip`, `.archive-list`, `.archive-card`, `.archive-tag`, `.archive-body`, `.archive-title`, `.archive-desc`, `.archive-meta`
- `.deliverables-section`, `.deliverables-grid`, `.deliv-card`, `.deliv-top`, `.deliv-status`, `.deliv-date`, `.deliv-title`, `.deliv-meta`
- `.feedback-feed`, `.feedback-feed-header`, `.feedback-list`, `.feedback-item`, `.feedback-item .fi-proj/fi-body/fi-head/fi-text`, `.feedback-empty`, `.feedback-loading`

### 2-5. 변경된 파일

- `0.NEWBIZ_MASTER/7.펜타/brainstorm/index.html` 만 수정 (총 ~270줄 추가/변경)
- 2번 push 완료:
  - `e5e86bf` — 기록 탭 통합 + 광역 피드백 피드 + 엔드포인트 trip2daniel 이전
  - `04d36dd` — 할일 탭 상단에 산출물 링크 카드 노출

---

## 3. 논의는 했지만 **미완**인 것 (다음 세션에서 이어갈 것)

### 3-1. 할일 시트 부풀림 해결 (가장 시급)

**문제**: 할일 시트에 항목이 쌓여서 Daniel이 실제로 안 보게 됨 → 시스템 실패

**제시된 해결 방향 3가지 (최종 합의 안 됨):**

#### ① "이번 주 움직일 것"만 할일에 진입 (권장)
- 담당·기한 모두 있고, 2주 안에 실제 손댈 것만
- 그 외는 로드맵 마일스톤 비고 또는 아이디어/기록으로
- 장점: 할일 탭이 항상 소수(10~15개 미만) 유지
- 단점: "언젠가 할 것" 저장 공간이 애매 (일단 로드맵 비고 활용)

#### ② 저장해줘 시 자동 청소 제안
- 새 항목 등록 전, 2주 이상 방치된 할일 리뷰 제안
- 선택지: 완료 / 삭제 / 다음 주로 기한 연기
- WIP 15개 상한 → 넘으면 추가 전에 강제 triage
- **구현 위치**: `~/.claude/CLAUDE.md`의 저장 프로토콜에 반영 (전 프로젝트 자동 적용)

#### ③ "나중에"와 "지금" 분리
- 할일 = 이번 주 + 다음 주
- "언젠가 할 것" = 아이디어 탭 (신규 카테고리 "미래 할일" 추가)
- 단점: 또 탭 늘어남 (단순화 철학과 충돌)

**Daniel이 최종 선택해야 할 것**: ①+② 추천했지만 미확정.

### 3-2. 펜타 할일 vs Daniel Flow 통합 보드 할일 구분

**문제**: 전역 CLAUDE.md 프로토콜은 "Daniel Flow 업무 보드"로 통합하라고 돼 있지만, 펜타 전용 작업은 펜타 보드가 맥락상 맞음.

**논의된 옵션:**
- A. 펜타 작업은 펜타 보드만
- B. 전부 Daniel Flow 보드만
- C. 양쪽 다 (중복)

**임시 결론 (미확정)**: A. 펜타는 펜타 보드, Daniel Flow 보드는 부서 간 조율 이슈만. 근데 확정 안 됨.

### 3-3. 기록 탭 개선 아이디어 (논의 초기 단계)

사용자 제안: **"상태 태그(아이디어/검토중/결정/합의)로 같은 카드의 상태만 바꾸면 됨"**

즉 현재는 아이디어 → 조사 → 의사결정 → 합의사항 탭 **이동**이 별개 레코드처럼 되는데, 같은 아이디어가 성숙해가는 **생애주기**를 하나의 카드 상태 전환으로 표현하자는 구상.

**구현 시 고민 지점:**
- 기존 5개 시트를 하나로 합쳐 "상태" 컬럼만 바꿀지?
- 아니면 시트는 그대로 두고 UI만 상태 전환으로 보여줄지?
- "이동" 버튼 (기존에 있음) 로직을 재활용 가능

### 3-4. 공지사항·리포트 광역 탭

현재는 자리만 있고 실제 렌더링 로직 확인 안 됨. 다음 세션에서:
- renderNoticePanel 현재 어떤 데이터 소스 쓰는지
- renderReportPanel이 산출물 갤러리로 진화할 수 있는지

---

## 4. 다음 세션 시작 시 참고 파일

| 경로 | 역할 |
|---|---|
| `0.NEWBIZ_MASTER/7.펜타/brainstorm/index.html` | 대시보드 메인 파일 (수정 대상) |
| `0.NEWBIZ_MASTER/7.펜타/brainstorm/DASHBOARD_SIMPLIFICATION.md` | 이 문서 (오늘 작업 노트) |
| Google Sheets `1pdW8Xif8ZA75UbkAAbnn02wosNbO5kNnmuJ462E-nqw` | 펜타 보드 SSOT |
| Service account key `~/Downloads/elem-writing-d09737ee13d7.json` | MCP 접근 막혔을 때 대체 경로 (python gspread/google-api-client) |

## 5. 작업 중 발견된 기술 이슈

### 5-1. MCP google-sheets 권한 문제
- 펜타 보드 시트 읽기/쓰기 시 "The caller does not have permission" 에러
- 원인: MCP가 쓰는 계정이 펜타 시트 편집자 공유에서 빠진 것으로 추정
- **해결**: service account(elem-writing-d09737ee13d7.json)로 python 직접 호출 → 성공
- **근본 해결 (다음 세션에서)**: 펜타 시트를 `brainstorm-sheets@elem-writing.iam.gserviceaccount.com` 또는 `donggil.lee@remarkedu.com`에 편집자로 다시 공유

### 5-2. escapeHtml 중복 정의
- 1103행·1944행 두 곳에 동일 함수 존재
- 동작엔 문제 없지만 정리 필요 (한 곳으로 통합)

### 5-3. 탭 정의 마이그레이션 안 됨
- 기존 탭들(아이디어/조사/의사결정/합의사항/회의록)이 SHEET_CONFIG에 여전히 존재
- UI에서는 안 보이지만 내부적으로 참조됨 (기록 탭이 이것들을 읽기 때문)
- **유지 필요**: 삭제하면 기록 통합 뷰 깨짐

---

## 6. 한 줄 요약 (다음 세션 문맥 부트스트랩용)

> 펜타보드를 10탭→3+2탭으로 급진 단순화. 할일 탭에 산출물·피드백 광역 스트립 추가. 할일 시트 부풀림 해결·탭 생애주기 상태화 논의는 미완.
