# 체크체크 수학 개념동영상 QR 체크

중학 수학 교재의 개념동영상 QR 코드를 한곳에 모아, **QR을 스캔하지 않아도 바로
개념 동영상을 볼 수 있게** 해주는 Streamlit 웹앱입니다. 학년·학기·단원별로 영상을
탐색하고 키워드로 검색할 수 있습니다.

## 데이터 흐름 한눈에 보기

```
교재 사진(qr_img/)                      ← 입력: 페이지를 찍은 jpg
  │  decode_qr.py  (QR → URL 추출)
  ▼
qr_output/*_raw.json                    ← 페이지별 URL 목록 (중간 산출물)
  │
  │  meta/*.tsv     (사람이 읽어 적은 단원·번호·쪽수·제목)
  ▼  build_catalog.py  (URL 산술 생성 + 메타 결합)
qr_*.json                               ← 앱이 읽는 구조화 데이터
  │  app.py  (Streamlit)
  ▼
웹앱 화면
```

핵심 사실: **QR 코드 안에는 URL만** 들어 있습니다. 단원명·영상 번호·쪽수·제목은
교재 지면에만 있으므로 `meta/*.tsv`에 따로 정리합니다. 또한 한 교재 안에서 QR의
코드값은 영상 번호와 **정확히 1씩 증가**하므로, URL은 `기준코드 + (번호-1)`로
산술 생성합니다(디코딩 누락이 있어도 번호만 알면 URL 복원 가능).

---

## 설치

```powershell
pip install -r requirements.txt
```

`requirements.txt`에는 앱 구동용 `streamlit`과 QR 디코딩용
`pdf2image`, `pyzbar`, `opencv-python-headless`, `numpy`, `pillow`가 들어 있습니다.

`pyzbar`와 `pdf2image`는 시스템 라이브러리가 추가로 필요합니다.

- **Windows**
  - `pyzbar`: 휠에 ZBar DLL이 포함되어 보통 별도 설치 불필요 (안 되면 Visual C++ 재배포 패키지 설치)
  - `pdf2image`(PDF 입력 시에만): [Poppler](https://github.com/oschwartz10612/poppler-windows) 설치 후 `bin`을 PATH에 추가
- **Streamlit Cloud / Debian**: `packages.txt`에 `libzbar0`, `poppler-utils`가 명시되어 배포 시 자동 설치됩니다.

---

## 1) 웹앱 실행 — `app.py`

같은 폴더의 `qr_*.json`(구조화 데이터)을 모두 읽어 학년·학기별로 보여줍니다.

```powershell
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 로 열립니다.

화면 기능
- **사이드바**: 학년·학기 선택, 단원 다중 선택 필터
- **키워드 검색**: 검색어 입력 시 전체 학년/학기에서 제목으로 검색
- **동영상 보기** 버튼: 해당 개념 동영상으로 이동

### 배포(Streamlit Community Cloud)
이 저장소는 GitHub(`plusminusji/git_practice`)에 연결되어 있고, master에 push하면
Streamlit Cloud가 **자동 재배포**합니다. 앱 구동에 필요한 파일은 `app.py`,
`qr_*.json`, `requirements.txt`, `packages.txt`입니다. (`qr_img/`, `qr_output/`,
`meta/`는 데이터 재생성용이며 앱 구동에는 불필요)

---

## 2) QR 코드 추출 — `decode_qr.py`

PDF 또는 이미지(jpg/jpeg/png)에서 QR 코드 URL을 추출해 `*_raw.json`으로 저장합니다.
사진 속 작은 QR이나 빛 반사로 흐린 QR도 잡도록 **확대 → Otsu/CLAHE 이진화 →
타일 분할 → OpenCV 다중 디텍터** 순으로 단계적으로 시도합니다.

```powershell
# 파일 하나 (pdf 또는 이미지)
python decode_qr.py qr_img/3-2/중3-2_1.jpg

# 여러 파일
python decode_qr.py a.pdf b.jpg c.png

# 디렉토리의 직속 파일
python decode_qr.py qr_img/3-2

# 디렉토리 + 하위 전체 재귀
python decode_qr.py qr_img -r

# 결과를 특정 폴더에 저장
python decode_qr.py qr_img -r -o qr_output

# PDF 변환 해상도 조정 (기본 300)
python decode_qr.py scan.pdf --dpi 400
```

| 옵션 | 설명 |
|------|------|
| `inputs` | pdf/이미지 파일 또는 디렉토리 (여러 개 가능) |
| `-r`, `--recursive` | 디렉토리 입력 시 하위 디렉토리까지 재귀 |
| `-o`, `--output` | 결과 JSON 저장 폴더 (미지정 시 입력 파일과 같은 위치) |
| `--dpi` | PDF를 이미지로 변환할 때의 해상도 (기본 300) |

출력 형식 — 페이지별 URL 리스트의 리스트:
```json
[
  ["http://code.chunjae.co.kr/qrcode/qrcode.aspx?qr=20210800407", "..."]
]
```

> **누락 점검 팁**: 한 교재의 코드는 연속이어야 합니다. 정렬했을 때 비는 코드가
> 있으면 그 QR이 인식되지 않은 것이니, 해당 이미지를 다시 인식하거나 확인하세요.

---

## 3) 앱 데이터 생성 — `build_catalog.py` + `meta/*.tsv`

`decode_qr.py`는 URL만 뽑으므로, 단원·번호·쪽수·제목을 입혀 앱용 구조화 JSON으로
바꿔야 합니다. 이 메타데이터는 **`meta/<학년>-<학기>.tsv`** 에 표로 적어둡니다.
`build_catalog.py`에는 하드코딩된 데이터가 없고, TSV를 읽어 JSON을 만드는 로직만 있습니다.

```powershell
python build_catalog.py
```

`meta/*.tsv`를 모두 읽어 각각 `qr_<학년>-<학기>.json`을 생성합니다.

### `meta/*.tsv` 형식 (탭 구분)
첫 줄은 책 단위 메타(주석), 둘째 줄은 컬럼 헤더, 이후는 데이터입니다.

```
# grade=3	semester=2	base=20210800407
chapter	number	page	title
1. 삼각비	1	p.10	삼각비의 뜻
1. 삼각비	2	p.12	30°, 45°, 60°의 삼각비의 값
2. 삼각비의 활용	6	p.28	직각삼각형에서 변의 길이
...
```

- `grade` / `semester`: 학년 / 학기
- `base`: 그 책 1번 영상의 QR 코드값 (URL = `base + 번호 - 1`)
- `chapter`: 단원명 (같은 값이 연속되면 한 단원으로 묶임, 등장 순서 유지)
- `number`: 책 전체에서 이어지는 영상 번호 (1부터, 빠짐없이 연속)
- `page` / `title`: 쪽수 / 영상 제목

> 제목·단원명에 쉼표가 많아 CSV 대신 **TSV(탭 구분)**를 씁니다.
> `build_catalog.py`는 번호가 `1..N`으로 연속인지 검사하며, 누락/중복이 있으면
> 에러로 알려줍니다.

### 생성되는 `qr_*.json`(앱 데이터) 형식
```json
{
  "book": "체크체크 수학 개념동영상 QR 체크",
  "total_videos": 29,
  "grade": 3,
  "semester": 2,
  "chapters": {
    "1. 삼각비": [
      { "number": 1, "page": "p.10", "title": "삼각비의 뜻",
        "url": "http://code.chunjae.co.kr/qrcode/qrcode.aspx?qr=20210800407" }
    ]
  }
}
```

---

## 새 교재 추가하기 (전체 워크플로)

1. 교재의 QR 페이지를 촬영해 `qr_img/<학년>-<학기>/`에 넣습니다.
2. QR을 추출합니다.
   ```powershell
   python decode_qr.py qr_img/2-1 -r -o qr_output
   ```
3. `qr_output/*_raw.json`의 코드 범위를 확인해 그 책의 **기준코드(가장 작은 코드)**
   와 영상 개수를 파악합니다. (코드가 연속이면 누락 없음)
4. `meta/2-1.tsv`를 만들어 단원·번호·쪽수·제목을 교재 지면에서 읽어 채웁니다.
   첫 줄에 `# grade=2\tsemester=1\tbase=<기준코드>`를 적습니다.
5. 앱 데이터를 생성합니다.
   ```powershell
   python build_catalog.py
   ```
6. `streamlit run app.py`로 확인 후 커밋·push하면 배포에 반영됩니다.

---

## 파일 구조

```
checkcheck/
├─ app.py                # Streamlit 웹앱 (qr_*.json을 읽어 표시)
├─ decode_qr.py          # 이미지/PDF → QR URL 추출 (qr_output/*_raw.json)
├─ build_catalog.py      # meta/*.tsv → qr_*.json 생성 (범용 변환기)
├─ requirements.txt      # 파이썬 의존성
├─ packages.txt          # 배포(Debian)용 시스템 라이브러리
├─ qr_1-1.json … qr_3-2.json   # 앱이 읽는 구조화 데이터 (학년-학기별)
├─ meta/                 # 단원·번호·쪽수·제목 데이터 (TSV, 학년-학기별)
│  ├─ 2-2.tsv
│  ├─ 3-1.tsv
│  └─ 3-2.tsv
├─ qr_img/               # 원본 교재 사진 (학년-학기 하위 폴더)
└─ qr_output/            # decode_qr.py 중간 산출물 (*_raw.json)
```
