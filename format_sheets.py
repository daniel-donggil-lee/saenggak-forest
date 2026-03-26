"""생각의숲 브레인스토밍 시트 서식 적용"""
import gspread
from gspread.utils import rowcol_to_a1

gc = gspread.service_account(filename='/Users/daniel/Downloads/elem-writing-d09737ee13d7.json')
ss = gc.open_by_key('1pdW8Xif8ZA75UbkAAbnn02wosNbO5kNnmuJ462E-nqw')

# 카테고리별 색상
CAT_COLORS = {
    '법인/거버넌스': {'red': 0.85, 'green': 0.92, 'blue': 1.0},
    '브랜드':       {'red': 1.0,  'green': 0.90, 'blue': 0.85},
    '콘텐츠':       {'red': 0.85, 'green': 1.0,  'blue': 0.88},
    '인력':         {'red': 1.0,  'green': 0.95, 'blue': 0.80},
    '시장/경쟁':    {'red': 0.93, 'green': 0.87, 'blue': 1.0},
    '사업 모델':    {'red': 0.90, 'green': 0.96, 'blue': 1.0},
    '마케팅':       {'red': 1.0,  'green': 0.88, 'blue': 0.88},
    '재무':         {'red': 0.88, 'green': 0.95, 'blue': 0.88},
}

HEADER_BG = {'red': 0.15, 'green': 0.15, 'blue': 0.20}
HEADER_FG = {'red': 1.0, 'green': 1.0, 'blue': 1.0}
DESC_BG = {'red': 0.95, 'green': 0.95, 'blue': 0.97}

SHEET_COL_WIDTHS = {
    '아이디어':   [100, 140, 250, 70, 120, 400],
    '조사':       [100, 180, 150, 70, 250, 400],
    '의사결정':   [100, 160, 60, 180, 120, 70, 400],
    '합의사항':   [100, 160, 300, 70, 400],
}

def get_sheet_id(title):
    for s in ss.fetch_sheet_metadata()['sheets']:
        if s['properties']['title'] == title:
            return s['properties']['sheetId']
    return None

def build_requests(sheet_title):
    ws = ss.worksheet(sheet_title)
    sid = get_sheet_id(sheet_title)
    if sid is None:
        return []

    data = ws.get_all_values()
    num_cols = len(SHEET_COL_WIDTHS.get(sheet_title, []))
    if num_cols == 0:
        return []

    requests = []

    # 1. 열 너비 설정
    for i, w in enumerate(SHEET_COL_WIDTHS[sheet_title]):
        requests.append({
            'updateDimensionProperties': {
                'range': {'sheetId': sid, 'dimension': 'COLUMNS', 'startIndex': i, 'endIndex': i + 1},
                'properties': {'pixelSize': w},
                'fields': 'pixelSize'
            }
        })

    # 2. Row 1 (설명) 서식
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': num_cols},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': DESC_BG,
                    'textFormat': {'fontSize': 10, 'italic': True, 'foregroundColor': {'red': 0.4, 'green': 0.4, 'blue': 0.4}},
                }
            },
            'fields': 'userEnteredFormat(backgroundColor,textFormat)'
        }
    })

    # 3. Row 2 (헤더) 서식 — 진한 배경 + 흰 글씨 + 볼드
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sid, 'startRowIndex': 1, 'endRowIndex': 2, 'startColumnIndex': 0, 'endColumnIndex': num_cols},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': HEADER_BG,
                    'textFormat': {'bold': True, 'fontSize': 10, 'foregroundColor': HEADER_FG},
                    'horizontalAlignment': 'CENTER',
                }
            },
            'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
        }
    })

    # 4. 행 고정 (2행)
    requests.append({
        'updateSheetProperties': {
            'properties': {'sheetId': sid, 'gridProperties': {'frozenRowCount': 2}},
            'fields': 'gridProperties.frozenRowCount'
        }
    })

    # 5. 데이터 행 — 카테고리별 배경색 (A열 기준)
    for row_idx in range(2, len(data)):
        cat = data[row_idx][0] if data[row_idx] else ''
        if cat in CAT_COLORS:
            requests.append({
                'repeatCell': {
                    'range': {'sheetId': sid, 'startRowIndex': row_idx, 'endRowIndex': row_idx + 1, 'startColumnIndex': 0, 'endColumnIndex': num_cols},
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': CAT_COLORS[cat],
                            'textFormat': {'fontSize': 10},
                            'wrapStrategy': 'WRAP',
                            'verticalAlignment': 'TOP',
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat,wrapStrategy,verticalAlignment)'
                }
            })
        elif cat == '':
            # 역할: 등 구분행 — 볼드 처리
            title_val = data[row_idx][1] if len(data[row_idx]) > 1 else ''
            if title_val.startswith('역할:') or title_val.startswith('역할 :'):
                requests.append({
                    'repeatCell': {
                        'range': {'sheetId': sid, 'startRowIndex': row_idx, 'endRowIndex': row_idx + 1, 'startColumnIndex': 0, 'endColumnIndex': num_cols},
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.92, 'green': 0.92, 'blue': 0.92},
                                'textFormat': {'bold': True, 'fontSize': 10},
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                })

    # 6. 카테고리 열 (A) — 볼드 + 센터
    if len(data) > 2:
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sid, 'startRowIndex': 2, 'endRowIndex': len(data), 'startColumnIndex': 0, 'endColumnIndex': 1},
                'cell': {
                    'userEnteredFormat': {
                        'textFormat': {'bold': True, 'fontSize': 9},
                        'horizontalAlignment': 'CENTER',
                        'verticalAlignment': 'TOP',
                    }
                },
                'fields': 'userEnteredFormat(textFormat,horizontalAlignment,verticalAlignment)'
            }
        })

    # 7. 전체 테두리
    requests.append({
        'updateBorders': {
            'range': {'sheetId': sid, 'startRowIndex': 1, 'endRowIndex': len(data), 'startColumnIndex': 0, 'endColumnIndex': num_cols},
            'top':    {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
            'bottom': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
            'left':   {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
            'right':  {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
            'innerHorizontal': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.9, 'green': 0.9, 'blue': 0.9}},
            'innerVertical':   {'style': 'SOLID', 'width': 1, 'color': {'red': 0.9, 'green': 0.9, 'blue': 0.9}},
        }
    })

    return requests

# 실행
all_requests = []
for sheet_name in ['아이디어', '조사', '의사결정', '합의사항']:
    print(f'  {sheet_name} 서식 생성 중...')
    all_requests.extend(build_requests(sheet_name))

print(f'\n총 {len(all_requests)}개 서식 요청 실행 중...')
ss.batch_update({'requests': all_requests})
print('완료!')
