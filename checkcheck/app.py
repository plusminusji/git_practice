import streamlit as st
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Page config
st.set_page_config(
    page_title="체크체크 수학 개념동영상",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1a1a2e;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .chapter-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
    }
    .video-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 16px;
        margin: 6px 0;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .video-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    .video-number {
        display: inline-block;
        background: #667eea;
        color: white;
        width: 32px;
        height: 32px;
        line-height: 32px;
        text-align: center;
        border-radius: 50%;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 10px;
    }
    .video-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1a1a2e;
    }
    .video-page {
        font-size: 0.8rem;
        color: #999;
        margin-top: 4px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 6px 20px;
        font-weight: 600;
        width: 100%;
    }
    .stats-box {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ── Load all available JSON files ──
def _get_json_fingerprint():
    """JSON 파일 목록과 수정 시각을 합쳐 fingerprint를 만든다.
    파일이 추가/수정/삭제되면 fingerprint가 달라져 캐시가 갱신된다."""
    files = sorted(BASE_DIR.glob("qr_*.json"))
    return tuple((f.name, f.stat().st_mtime) for f in files)


@st.cache_data
def load_all_data(_fingerprint):
    """qr_*.json 파일을 모두 읽어서 {표시이름: data} 딕셔너리로 반환"""
    catalog = {}
    for f in sorted(BASE_DIR.glob("qr_*.json")):
        with open(f, "r", encoding="utf-8") as fp:
            d = json.load(fp)
        grade = d.get("grade", "?")
        semester = d.get("semester", "?")
        label = f"중{grade} - {semester}학기"
        catalog[label] = d
    return catalog


catalog = load_all_data(_fingerprint=_get_json_fingerprint())

if not catalog:
    st.error("📂 qr_*.json 파일을 찾을 수 없습니다. app.py와 같은 폴더에 넣어주세요.")
    st.stop()

# ── Sidebar: 학년·학기 선택 ──
st.sidebar.title("🎓 학년 · 학기")
selected_label = st.sidebar.radio(
    "학년/학기를 선택하세요",
    options=list(catalog.keys()),
)

data = catalog[selected_label]
grade = data.get("grade", "")
semester = data.get("semester", "")

# ── Sidebar: 챕터 필터 ──
st.sidebar.markdown("---")
st.sidebar.title("📚 챕터 선택")
chapters = list(data["chapters"].keys())
selected_chapters = st.sidebar.multiselect(
    "보고 싶은 챕터를 선택하세요",
    chapters,
    default=chapters,
    placeholder="전체 선택됨",
)

# ── Sidebar: 키워드 검색 ──
search = st.sidebar.text_input("🔍 키워드 검색", placeholder="예: 삼각형, 부채꼴...")

# ── Header ──
st.markdown('<div class="main-title">🎯 체크체크 수학 개념동영상</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-title">중학 {grade}학년 {semester}학기 · QR 체크 — 이해가 안 될 때 바로 보세요!</div>',
    unsafe_allow_html=True,
)

# ── Stats ──
total_shown = sum(len(data["chapters"][ch]) for ch in selected_chapters)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("전체 동영상", f"{data['total_videos']}개")
with col2:
    st.metric("선택된 챕터", f"{len(selected_chapters)}개")
with col3:
    st.metric("표시 중", f"{total_shown}개")

st.divider()

# ── Display videos ──
for chapter in selected_chapters:
    items = data["chapters"][chapter]

    if search:
        items = [item for item in items if search.lower() in item["title"].lower()]

    if not items:
        continue

    st.markdown(f'<div class="chapter-header">📖 {chapter}</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    for i, item in enumerate(items):
        with cols[i % 4]:
            with st.container():
                st.markdown(f"""
                <div class="video-card">
                    <span class="video-number">{item['number']:02d}</span>
                    <span class="video-title">{item['title']}</span>
                    <div class="video-page">📄 {item['page']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.link_button(
                    "▶️ 동영상 보기",
                    item["url"],
                    use_container_width=True,
                )

# ── Footer ──
st.divider()
st.caption("📱 QR 코드를 스캔하지 않아도 바로 개념 동영상을 볼 수 있습니다. | 체크체크 수학 개념동영상 QR 체크")