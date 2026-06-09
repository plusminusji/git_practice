# -*- coding: utf-8 -*-
"""meta/<grade>-<semester>.tsv 의 메타데이터로 app.py가 쓰는
구조화 JSON(qr_<grade>-<semester>.json)을 생성한다.

메타데이터(단원/번호/쪽수/제목)는 QR에 없고 교재 지면에만 있으므로
사람이 읽어 meta/*.tsv 에 표 형태로 적어둔다. 이 스크립트에는
하드코딩된 데이터가 없으며, TSV를 읽어 JSON으로 변환하는 로직만 담는다.

TSV 형식:
    # grade=3\tsemester=2\tbase=20210800407   <- 첫 줄: 책 단위 메타(주석)
    chapter\tnumber\tpage\ttitle               <- 헤더
    1. 삼각비\t1\tp.10\t삼각비의 뜻             <- 데이터 ...

핵심 전제(데이터로 검증됨): 한 교재 안에서 QR 코드값은 영상 번호와
정확히 1씩 증가한다. 따라서 url = base + (number - 1) 로 산술 생성한다.
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
META_DIR = BASE_DIR / "meta"
BOOK_TITLE = "체크체크 수학 개념동영상 QR 체크"
URL_FMT = "http://code.chunjae.co.kr/qrcode/qrcode.aspx?qr={code}"


def parse_header(line):
    """'# grade=3\tsemester=2\tbase=...' 주석 줄을 dict로 파싱."""
    fields = line.lstrip("#").strip().split("\t")
    meta = {}
    for f in fields:
        k, _, v = f.partition("=")
        meta[k.strip()] = int(v.strip())
    return meta


def load_tsv(path):
    """TSV 한 개를 읽어 app용 구조화 dict로 변환."""
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = [ln for ln in lines if ln.strip()]
    header_meta = parse_header(rows[0])           # 첫 줄: 책 메타
    base = header_meta["base"]
    grade, semester = header_meta["grade"], header_meta["semester"]
    # rows[1] 은 컬럼 헤더(chapter/number/page/title) → 건너뜀

    chapters = {}        # 단원명 -> [item] (등장 순서 유지)
    numbers = []
    for ln in rows[2:]:
        chapter, number, page, title = ln.split("\t")
        number = int(number)
        numbers.append(number)
        chapters.setdefault(chapter, []).append({
            "number": number,
            "page": page,
            "title": title,
            "url": URL_FMT.format(code=base + number - 1),
        })

    # 무결성 검사: 번호가 1..N 으로 빠짐없이 연속인지
    expected = list(range(1, len(numbers) + 1))
    if sorted(numbers) != expected:
        missing = sorted(set(expected) - set(numbers))
        raise ValueError(f"{path.name}: 영상 번호가 1~{len(numbers)} 연속이 아닙니다. "
                         f"누락/중복 확인 필요 (누락 추정: {missing})")

    return grade, semester, {
        "book": BOOK_TITLE,
        "total_videos": len(numbers),
        "grade": grade,
        "semester": semester,
        "chapters": chapters,
    }


def main():
    tsv_files = sorted(META_DIR.glob("*.tsv"))
    if not tsv_files:
        print(f"메타데이터 파일이 없습니다: {META_DIR}/*.tsv")
        return
    for path in tsv_files:
        grade, semester, data = load_tsv(path)
        out = BASE_DIR / f"qr_{grade}-{semester}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"{path.name} -> {out.name}: {data['total_videos']}개 영상, "
              f"{len(data['chapters'])}개 단원")


if __name__ == "__main__":
    main()
