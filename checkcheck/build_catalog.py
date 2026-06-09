# -*- coding: utf-8 -*-
"""decode_qr.py가 뽑은 URL(코드)에 교재에서 읽은 메타데이터를 입혀
app.py가 쓰는 구조화 JSON(qr_<g>-<s>.json)을 생성한다.

핵심 전제(데이터로 검증됨): 한 교재 안에서 QR 코드값은 영상 번호와
정확히 1씩 증가한다. 즉 URL = BASE_URL + (기준코드 + 번호 - 1).
따라서 번호만 알면 URL을 산술적으로 만들 수 있어, QR 디코딩 누락과
무관하게 누락 없는 카탈로그를 만들 수 있다.

메타데이터(단원/쪽수/제목)는 QR에 없고 교재 지면에 있으므로 아래
표에 직접 채운다. (이미지에서 읽어 입력)
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
BOOK_TITLE = "체크체크 수학 개념동영상 QR 체크"
URL_FMT = "http://code.chunjae.co.kr/qrcode/qrcode.aspx?qr={code}"

# 책별 정의: (grade, semester, 기준코드, [(단원명, [(번호, 쪽수, 제목), ...]), ...])
BOOKS = [
    {
        "grade": 3, "semester": 2, "base": 20210800407,
        "chapters": [
            ("1. 삼각비", [
                (1, "p.10", "삼각비의 뜻"),
                (2, "p.12", "30°, 45°, 60°의 삼각비의 값"),
                (3, "p.14", "예각의 삼각비의 값"),
                (4, "p.14", "0°, 90°의 삼각비의 값"),
                (5, "p.15", "삼각비의 표를 이용한 삼각비의 값"),
            ]),
            ("2. 삼각비의 활용", [
                (6, "p.28", "직각삼각형에서 변의 길이"),
                (7, "p.29", "일반 삼각형에서 변의 길이"),
                (8, "p.30", "일반 삼각형의 높이"),
                (9, "p.32", "삼각비의 활용 - 삼각형의 넓이"),
                (10, "p.33", "삼각비의 활용 - 사각형의 넓이"),
            ]),
            ("3. 원과 직선", [
                (11, "p.45", "원의 중심과 현의 수직이등분선"),
                (12, "p.46", "원의 중심과 현의 길이"),
                (13, "p.49", "원의 접선"),
                (14, "p.50", "삼각형의 내접원과 접선"),
                (15, "p.51", "사각형의 내접원과 접선"),
            ]),
            ("4. 원주각", [
                (16, "p.65~66", "원주각과 중심각의 크기"),
                (17, "p.66", "반원에 대한 원주각의 크기"),
                (18, "p.67", "원주각의 크기와 호의 길이"),
                (19, "p.70", "네 점이 한 원 위에 있을 조건"),
                (20, "p.71", "원에 내접하는 사각형의 성질"),
                (21, "p.72", "사각형이 원에 내접하기 위한 조건"),
                (22, "p.75", "원의 접선과 현이 이루는 각"),
                (23, "p.76", "두 원에서 공통인 접선과 현이 이루는 각"),
            ]),
            ("5. 통계", [
                (24, "p.89", "대푯값"),
                (25, "p.90", "중앙값"),
                (26, "p.91", "최빈값"),
                (27, "p.94~95", "산포도, 편차"),
                (28, "p.96", "분산과 표준편차"),
                (29, "p.99~100", "산점도와 상관관계"),
            ]),
        ],
    },
]


def build(book):
    base = book["base"]
    chapters = {}
    total = 0
    for ch_name, items in book["chapters"]:
        rows = []
        for number, page, title in items:
            rows.append({
                "number": number,
                "page": page,
                "title": title,
                "url": URL_FMT.format(code=base + number - 1),
            })
            total += 1
        chapters[ch_name] = rows
    return {
        "book": BOOK_TITLE,
        "total_videos": total,
        "grade": book["grade"],
        "semester": book["semester"],
        "chapters": chapters,
    }


def main():
    for book in BOOKS:
        data = build(book)
        out = BASE_DIR / f"qr_{book['grade']}-{book['semester']}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"{out.name}: {data['total_videos']}개 영상, "
              f"{len(data['chapters'])}개 단원 -> 저장 완료")


if __name__ == "__main__":
    main()
