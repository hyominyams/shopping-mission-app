import streamlit as st

# 페이지 설정
st.set_page_config(page_title="합리적 소비 미션", layout="wide")

st.title("🛍️ 합리적 소비 장보기 미션")

# 예산 설정
BUDGET = 30000

# 세션 초기화
if "mission" not in st.session_state:
    st.session_state.mission = None
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "quantities" not in st.session_state:
    st.session_state.quantities = {}

# 미션 선택
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
        st.rerun()
else:
    st.subheader(f"🎯 미션: {st.session_state.mission}")
    st.caption(missions[st.session_state.mission])

    # 상품 목록
    products = [
        {
            "id": "onion_1",
            "name": "양파 (1개)",
            "price": 500,
            "image": "https://png.pngtree.com/png-clipart/20210311/original/pngtree-onion-png-image_6001491.jpg",
        },
        {
            "id": "onion_3",
            "name": "양파 (3개)",
            "price": 1200,
            "image": "https://png.pngtree.com/png-clipart/20210311/original/pngtree-onion-png-image_6001491.jpg",
        },
        # 여기에 더 많은 상품 추가 가능
    ]

    st.subheader("2️⃣ 상품을 골라 담아보세요!")
    cols = st.columns(3)

    for i, item in enumerate(products):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {item['name']}")
                st.image(item["image"], width=100)
                st.markdown(f"💰 **{item['price']}원**", unsafe_allow_html=True)

                qty = st.session_state.quantities.get(item["id"], 1)

                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("➖", key=f"dec_{item['id']}") and qty > 1:
                        st.session_state.quantities[item["id"]] = qty - 1
                        st.rerun()
                with col2:
                    st.markdown(f"**{qty}개**")
                with col3:
                    if st.button("➕", key=f"inc_{item['id']}"):
                        st.session_state.quantities[item["id"]] = qty + 1
                        st.rerun()

                if st.button("🛒 담기", key=f"add_{item['id']}"):
                    if item["id"] in st.session_state.cart:
                        st.session_state.cart[item["id"]]["qty"] += qty
                    else:
                        st.session_state.cart[item["id"]] = {
                            "name": item["name"],
                            "price": item["price"],
                            "qty": qty,
                            "image": item["image"],
                        }
                    st.success(f"{item['name']} {qty}개 담았어요!")
                    st.rerun()

    # 장바구니
    st.subheader("3️⃣ 장바구니 확인 및 제출")

    if not st.session_state.cart:
        st.info("장바구니가 비어 있어요.")
    else:
        total = 0
        for pid, item in st.session_state.cart.items():
            subtotal = item["price"] * item["qty"]
            total += subtotal

            col1, col2, col3 = st.columns([1, 5, 1])
            with col1:
                st.image(item["image"], width=50)
            with col2:
                st.markdown(
                    f"""**{item['name']}**  
                    👉 **{item['qty']}개** × {item['price']}원  
                    = 💰 **{subtotal}원**"
                    """,
                    unsafe_allow_html=True
                )
            with col3:
                if st.button("❌", key=f"remove_{pid}"):
                    del st.session_state.cart[pid]
                    st.rerun()

        st.markdown(f"### 🧾 총합: **{total}원**")
        st.markdown(f"### 💰 잔액: **{BUDGET - total}원**")

        if st.button("제출하고 결과 보기"):
            st.session_state.submitted = True
            st.rerun()

    if "submitted" in st.session_state and st.session_state.submitted:
        st.subheader("4️⃣ 결과 확인")
        total = sum(item["price"] * item["qty"] for item in st.session_state.cart.values())
        remaining = BUDGET - total

        st.success(f"총 {total}원을 사용했습니다.")
        st.info(f"잔액은 {remaining}원입니다.")

        st.markdown("📝 결과를 보고 용돈기입장에 작성해보세요!")

        if st.button("🔁 다시 시작하기"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
