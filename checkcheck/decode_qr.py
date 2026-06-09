import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode, ZBarSymbol
from PIL import Image

# 지원하는 입력 확장자
PDF_EXTS = {".pdf"}
IMG_EXTS = {".jpg", ".jpeg", ".png"}
SUPPORTED_EXTS = PDF_EXTS | IMG_EXTS


def _pyzbar(arr):
    """numpy(grayscale 또는 RGB) 배열에서 QR URL 목록을 반환한다."""
    return [q.data.decode("utf-8")
            for q in decode(arr, symbols=[ZBarSymbol.QRCODE])]


def decode_image(img):
    """PIL 이미지 한 장에서 QR 코드 URL을 추출한다.

    사진으로 찍은 페이지는 QR이 작거나 빛 반사로 흐려서 원본 1배로는
    인식이 안 되는 경우가 많다. 그래서 단계적으로 강도를 높여가며 시도하고,
    찾은 URL을 (등장 순서를 유지한 채) 중복 제거하여 반환한다.

    1) 원본을 여러 배율로 확대
    2) 확대본에 Otsu / CLAHE+Otsu 이진화
    3) 그래도 부족하면 타일로 잘라 각 조각을 확대·이진화 (작은 QR 대응)
    4) 보조로 OpenCV 다중 QR 디텍터
    """
    found = {}  # url -> True (삽입 순서 유지용 dict)

    def add(urls):
        for u in urls:
            found.setdefault(u, True)

    rgb = np.array(img.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    H, W = gray.shape
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))

    # 1) 전체 이미지 여러 배율 + 이진화
    for scale in (1, 2, 3, 4):
        big = cv2.resize(gray, (W * scale, H * scale),
                         interpolation=cv2.INTER_LANCZOS4) if scale > 1 else gray
        add(_pyzbar(big))
        _, otsu = cv2.threshold(big, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        add(_pyzbar(otsu))
        _, ceq = cv2.threshold(clahe.apply(big), 0, 255,
                               cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        add(_pyzbar(ceq))

    # 2) 타일 분할 (4x4, 50% 겹침) — 한 페이지에 작은 QR이 여러 개일 때
    cols, rows = 4, 4
    tw, th = W // cols, H // rows
    step_x, step_y = max(tw // 2, 1), max(th // 2, 1)
    for top in range(0, max(H - th, 0) + 1, step_y):
        for left in range(0, max(W - tw, 0) + 1, step_x):
            tile = gray[top:top + th, left:left + tw]
            big = cv2.resize(tile, (tw * 4, th * 4),
                             interpolation=cv2.INTER_LANCZOS4)
            add(_pyzbar(big))
            _, otsu = cv2.threshold(big, 0, 255,
                                    cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            add(_pyzbar(otsu))
            _, ceq = cv2.threshold(clahe.apply(big), 0, 255,
                                   cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            add(_pyzbar(ceq))

    # 3) OpenCV 다중 QR 디텍터 (보조)
    ok, decoded, _, _ = cv2.QRCodeDetector().detectAndDecodeMulti(rgb)
    if ok:
        add([d for d in decoded if d])

    return list(found.keys())


def extract_qr(path, dpi=300):
    """PDF 또는 이미지 파일에서 QR 코드 URL을 추출한다.

    반환값은 페이지별 URL 리스트의 리스트.
    이미지는 페이지가 1개이므로 [[url, ...]] 형태가 된다.
    """
    ext = path.suffix.lower()
    print(f"\n=== Processing: {path} ===")

    if ext in PDF_EXTS:
        images = convert_from_path(str(path), dpi=dpi)
    elif ext in IMG_EXTS:
        images = [Image.open(path)]
    else:
        print(f"  지원하지 않는 형식이라 건너뜁니다: {ext}")
        return []

    all_urls = []
    for i, img in enumerate(images):
        page_urls = decode_image(img)
        all_urls.append(page_urls)
        print(f"\nPage {i + 1}:")
        if page_urls:
            for url in page_urls:
                print(f"  QR: {url}")
        else:
            print("  (QR 없음)")
    return all_urls


def collect_inputs(raw_paths, recursive):
    """입력 경로(파일/디렉토리)들을 실제 처리할 파일 목록으로 펼친다.

    - 파일이면 그대로 추가
    - 디렉토리이면 recursive 여부에 따라 하위 모든/직속 pdf·jpg 파일을 수집
    """
    files = []
    for raw in raw_paths:
        p = Path(raw)
        if not p.exists():
            print(f"경로를 찾을 수 없습니다: {p}", file=sys.stderr)
            continue
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            globber = p.rglob("*") if recursive else p.glob("*")
            matched = sorted(
                f for f in globber
                if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS
            )
            if not matched:
                print(f"디렉토리에서 처리할 파일을 찾지 못했습니다: {p}", file=sys.stderr)
            files.extend(matched)
    return files


def output_path_for(input_file, output, base_inputs):
    """결과 JSON을 저장할 경로를 결정한다.

    output 미지정: 입력 파일과 같은 위치
    output 디렉토리: 그 안에 <파일이름>_raw.json
    """
    name = f"{input_file.name}_raw.json"
    if output is None:
        return input_file.with_name(name)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    return out / name


def main():
    parser = argparse.ArgumentParser(
        description="PDF/JPG 파일 또는 디렉토리에서 QR 코드 URL을 추출한다."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="입력 경로 (pdf/jpg 파일 또는 디렉토리, 여러 개 가능)",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="디렉토리 입력 시 하위 모든 디렉토리까지 재귀적으로 처리",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="결과 JSON을 저장할 디렉토리 (미지정 시 입력 파일과 같은 위치)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="PDF를 이미지로 변환할 때의 해상도 (기본 300)",
    )
    args = parser.parse_args()

    files = collect_inputs(args.inputs, args.recursive)
    if not files:
        print("처리할 파일이 없습니다.", file=sys.stderr)
        sys.exit(1)

    print(f"처리 대상 파일 {len(files)}개")
    for f in files:
        results = extract_qr(f, dpi=args.dpi)
        out_path = output_path_for(f, args.output, args.inputs)
        with open(out_path, "w", encoding="utf-8") as fp:
            json.dump(results, fp, indent=2, ensure_ascii=False)
        print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
