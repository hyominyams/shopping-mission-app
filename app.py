import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import requests, datetime, traceback
from io import BytesIO
from collections import OrderedDict

# ───────────────────────── 공통 설정 ─────────────────────────
st.set_page_config(page_title="합리적 소비 미션", layout="wide")
st.title("🏍️ 합리적 소비 장보기 미션")

# safe_rerun: 버전에 따라 st.rerun / st.experimental_rerun
def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# 세션 상태 초기화
if "mission" not in st.session_state:
    st.session_state.update(
        mission=None, cart={}, quantities={},
        submitted=False, reason="", reason_submitted=False,
        budget=0
    )

# ───────────────────────── 카테고리 자동 분류 ─────────────────────────
FOOD_KW = [
    "양파", "감자", "당근", "돼지고기", "소고기", "카레", "햇반", "쌀", "식용유", "마늘",
    "김밥", "과일", "샌드위치", "생수", "주스", "컵라면", "라면", "과자", "음료",
    "케이크", "조각", "탄산", "생일초"
]
LIFE_KW = [
    "칫솔", "치약", "세면도구", "물티슈", "보조배터리", "귀마개", "슬리퍼", "우산",
    "양말", "손세정제", "비누", "쓰레기", "비상약", "물병", "썬크림", "모기",
    "수저", "재사용"
]
CATEGORY_ORDER = ["식품코너", "생활용품코너", "기타 잡화코너"]

def classify(name: str) -> str:
    for kw in FOOD_KW:
        if kw in name:
            return "식품코너"
    for kw in LIFE_KW:
        if kw in name:
            return "생활용품코너"
    return "기타 잡화코너"

# ───────────────────────── 데이터 로드 ─────────────────────────
@st.cache_data
def load_products(path: str):
    df = pd.read_excel(path).dropna(subset=["상품명", "가격", "이미지_URL"])
    products = []
    for i, r in df.iterrows():
        name = str(r["상품명"])
        products.append({
            "id": f"item_{i}",
            "name": name,
            "price": int(r["가격"]),
            "image": r["이미지_URL"],
            "category": classify(name)
        })
    return products

products = load_products("상품목록_이미지입력용.xlsx")

# ───────────────────────── 미션 데이터 ─────────────────────────
missions = OrderedDict({
    "우리 가족을 위한 카레라이스 만들기 🍛 [30,000원]": {
        "budget": 30_000,
        "desc": "우리 가족(4명)이 배부를게 먹을 수 있는 양의 카레라이스 만들어봅시다!"
    },
    "여름 캠핑 준비하기 🏕️ [40,000원]": {
        "budget": 40_000,
        "desc": "가족과 함께 1박2일로 캠핑을 떠납니다! 꼭 필요한 물건을 준비해보세요."
    },
    "친구 생일 파티 준비하기 🎉 [40,000원]": {
        "budget": 40_000,
        "desc": "친구의 생일을 축하하고, 파티를 즐기기 위한 준비를 해봅시다."
    }
})

# ───────────────────────── 1. 미션 선택 ─────────────────────────
if not st.session_state.mission and not st.session_state.submitted:
    st.subheader("1️⃣ 미션을 선택하세요")
    mission_choice = st.radio("미션 선택:", list(missions.keys()))
    if st.button("미션 시작하기"):
        st.session_state.mission = mission_choice
        st.session_state.budget = missions[mission_choice]["budget"]
        safe_rerun()

# ───────────────────────── 2. 상품 담기 화면 ─────────────────────────
elif not st.session_state.submitted:
    current_mission = st.session_state.mission
    budget = st.session_state.budget

    st.subheader(f"🎯 미션: {current_mission}")
    st.caption(missions[current_mission]["desc"])

    st.subheader("2️⃣ 상품을 골라 담아보세요!")

    FIXED_CARD_H = 300   # 카드 높이 고정

    # 카테고리별로 제품 정렬
    categories = OrderedDict((c, []) for c in CATEGORY_ORDER)
    for p in products:
        cat = p["category"] if p["category"] in CATEGORY_ORDER else "기타 잡화코너"
        categories[cat].append(p)

    for cat, items in categories.items():
        if not items:
            continue
        st.markdown(f"### 📂 {cat}")
        for idx, item in enumerate(items):
            if idx % 3 == 0:
                cols = st.columns(3)

            with cols[idx % 3]:
                with st.container(border=True):
                    # --- 카드(상품명·이미지·가격) ---
                    card_html = f"""
                    <div style="
                        height:{FIXED_CARD_H - 100}px;
                        display:flex; flex-direction:column; justify-content:space-between;
                        align-items:center; padding:6px 4px;">
                        <div style='font-weight:bold; text-align:center; min-height:40px;'>{item['name']}</div>
                        <img src='{item['image']}' style='width:110px; height:110px; object-fit:contain; border:1px solid #eaeaea;'>
                        <div style='font-size:16px; text-align:center;'>💰 <strong>{item['price']}원</strong></div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

                    # --- 수량/담기 컨트롤 (위젯 상태 활용) ---
                    qty_key = f"qty_{item['id']}"
                    if qty_key not in st.session_state:
                        st.session_state[qty_key] = 1  # 초기화

                    qty = st.number_input(
                        "수량", min_value=1, step=1, key=qty_key,
                        label_visibility="collapsed"
                    )

                    # 최신 수량을 quantities dict에도 반영
                    st.session_state.quantities[item["id"]] = qty

                    if st.button("🛒 담기", key=f"add_{item['id']}"):
                        cart = st.session_state.cart
                        if item["id"] in cart:
                            cart[item["id"]]["qty"] = qty  # 선택 수량으로 덮어쓰기
                        else:
                            cart[item["id"]] = {
                                "name": item["name"], "price": item["price"],
                                "qty": qty, "image": item["image"]
                            }
                        st.toast(f"{item['name']} {qty}개 담았습니다.", icon="🛒")

    # ───────────── 3. 장바구니 & 제출 ─────────────
    st.subheader("3️⃣ 장바구니 확인 및 제출")
    cart, total = st.session_state.cart, 0

    if not cart:
        st.info("장바구니가 비어 있어요.")
    else:
        for pid, it in cart.items():
            subtotal = it["price"] * it["qty"]
            total += subtotal
            col1, col2, col3 = st.columns([1, 5, 1])
            with col1:
                st.image(it["image"], width=50)
            with col2:
                st.markdown(
                    f"<div style='display:flex; flex-direction:column; align-items:flex-start;'>"
                    f"<span style='font-weight:600'>{it['name']}</span>"
                    f"<span>👉 {it['qty']}개 × {it['price']}원 = <strong>{subtotal}원</strong></span>"
                    "</div>", unsafe_allow_html=True
                )
            with col3:
                if st.button("❌", key=f"remove_{pid}"):
                    del cart[pid]
                    safe_rerun()

        st.markdown(f"### 🧾 총합: **{total:,} 원**")
        st.markdown(f"### 💰 잔액: **{budget - total:,} 원**")

        if total > budget:
            st.error("예산을 초과했습니다! 장바구니를 조정해 주세요.")
        elif st.button("제출하고 결과 보기"):
            st.session_state.submitted = True
            safe_rerun()

# ───────────────────────── 4. 결과 확인 ─────────────────────────
elif st.session_state.submitted:
    cart = st.session_state.cart
    budget = st.session_state.budget
    total = sum(it["price"] * it["qty"] for it in cart.values())
    remaining = budget - total

    st.subheader("4️⃣ 결과 확인")
    st.success(f"총 {total:,}원을 사용했습니다.")
    st.info(f"잔액은 {remaining:,}원입니다.")

    st.markdown("## 🛍️ 내가 구매한 물품")
    for it in cart.values():
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(it["image"], width=70)
            with col2:
                st.markdown(
                    f"<div style='display:flex; flex-direction:column; align-items:flex-start;'>"
                    f"<span style='font-weight:600'>{it['name']}</span>"
                    f"<span>{it['qty']}개 / 개당 {it['price']}원</span>"
                    "</div>", unsafe_allow_html=True
                )

    # 구매 이유
    st.markdown("### ✍️ 구매한 이유를 적어보세요:")
    reason = st.text_area(
        "", value=st.session_state.get("reason", ""),
        placeholder="왜 이 물건들을 샀나요? 어떤 기준으로 선택했나요?", height=100
    )
    if st.button("구매 이유 제출"):
        st.session_state.update(reason=reason, reason_submitted=True)
        st.toast("구매 이유가 저장되었습니다.", icon="✅")

    # ───────────── PNG 다운로드 ─────────────
    if st.session_state.reason_submitted:
        st.markdown("## ✅ 결과 다운로드")
        try:
            font_path = "NanumHumanRegular.ttf"
            font = ImageFont.truetype(font
