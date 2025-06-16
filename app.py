import streamlit as st

# --------------------------
# 기본 설정
# --------------------------
st.set_page_config(page_title="합리적 소비 미션", page_icon="🛍️", layout="wide")
st.title("🛒 합리적 소비 장보기 미션")

# 초기 세션 상태
if "mission" not in st.session_state:
    st.session_state.mission = None
if "cart" not in st.session_state:
    st.session_state.cart = []

BUDGET = 30000  # 예산

# --------------------------
# 미션 선택
# --------------------------
missions = {
    "카레라이스 만들기 🍛": "카레에 필요한 재료를 선택해보세요!",
    "해외여행 준비 ✈️": "여행 가기 전 필요한 물건을 준비하세요!",
    "소풍 도시락 준비 🎒": "소풍에 가져갈 도시락과 준비물을 선택하세요!"
}

if not st.session_state.mission:
    st.subheader("1️⃣ 미션을 선택하세요")
    mission_choice = st.radio("미션 선택:", list(missions.keys()))
    if st.button("미션 시작하기"):
        st.session_state.mission = mission_choice
        st.experimental_rerun()
else:
    st.subheader(f"🎯 미션: {st.session_state.mission}")
    st.caption(missions[st.session_state.mission])

    # --------------------------
    # 상품 목록
    # --------------------------
    st.subheader("2️⃣ 상품을 선택해 장바구니에 담으세요")

    products = [
        {"name": "양파 (1개)", "price": 500, "emoji": "🧅"},
        {"name": "양파 (3개)", "price": 1200, "emoji": "🧅"},
        {"name": "당근 (1개)", "price": 600, "emoji": "🥕"},
        {"name": "감자 (2개)", "price": 1100, "emoji": "🥔"},
        {"name": "고기 (팩)", "price": 5000, "emoji": "🥩"},
        {"name": "카레가루", "price": 2000, "emoji": "🍛"},
        {"name": "여권 케이스", "price": 3000, "emoji": "📘"},
        {"name": "칫솔", "price": 1000, "emoji": "🪥"},
        {"name": "여행용 가방", "price": 15000, "emoji": "🧳"},
        {"name": "물티슈", "price": 1000, "emoji": "🧻"},
        {"name": "김밥", "price": 2500, "emoji": "🍙"},
        {"name": "과일 도시락", "price": 4000, "emoji": "🍓"},
        {"name": "물", "price": 800, "emoji": "🥤"},
        {"name": "샌드위치", "price": 3000, "emoji": "🥪"},
        {"name": "모자", "price": 7000, "emoji": "🧢"},
        {"name": "선크림", "price": 5000, "emoji": "🧴"},
        {"name": "우산", "price": 4000, "emoji": "☔"},
        {"name": "카메라", "price": 25000, "emoji": "📷"},
        {"name": "비누", "price": 1200, "emoji": "🧼"},
        {"name": "세면도구 세트", "price": 4500, "emoji": "🪒"},
        {"name": "반찬통", "price": 3500, "emoji": "🥡"},
        {"name": "수저세트", "price": 1000, "emoji": "🥢"},
        {"name": "냅킨", "price": 700, "emoji": "🧻"},
    ]

    cols = st.columns(4)
    for i, item in enumerate(products):
        with cols[i % 4]:
            st.markdown(f"{item['emoji']} **{item['name']}**")
            st.markdown(f"💰 {item['price']}원")
            if st.button(f"담기 ➕", key=f"add_{i}"):
                st.session_state.cart.append(item)

    # --------------------------
    # 장바구니
    # --------------------------
    st.subheader("3️⃣ 장바구니 확인 및 제출")
    if not st.session_state.cart:
        st.info("장바구니가 비어 있습니다.")
    else:
        total = sum(item["price"] for item in st.session_state.cart)
        for item in st.session_state.cart:
            st.markdown(f"- {item['emoji']} {item['name']} ({item['price']}원)")
        st.markdown(f"**총합: {total}원** / 예산: {BUDGET}원")

        if st.button("🧾 제출하고 결과 보기"):
            st.session_state.submitted = True

    # --------------------------
    # 결과 화면
    # --------------------------
    if "submitted" in st.session_state and st.session_state.submitted:
        st.subheader("4️⃣ 결과")
        total = sum(item["price"] for item in st.session_state.cart)
        remaining = BUDGET - total
        st.success(f"총 {total}원을 사용했습니다.")
        st.info(f"잔액: {remaining}원")
        st.markdown("---")
        st.markdown("📝 이 결과를 보고 용돈기입장에 작성하세요.")
        if st.button("🔁 다시 시작"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.experimental_rerun()
