import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import time

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
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# 미션 선택
missions = {
    "카레라이스 만들기 🍛": "카레에 필요한 재료를 선택해보세요!",
    "해외여행 준비 ✈️": "여행 가기 전 필요한 물건을 준비하세요!",
    "소풍 도시락 준비 🎒": "소풍에 가져갈 도시락과 준비물을 선택하세요!"
}

if not st.session_state.mission and not st.session_state.submitted:
    st.subheader("1️⃣ 미션을 선택하세요")
    mission_choice = st.radio("미션 선택:", list(missions.keys()))
    if st.button("미션 시작하기"):
        st.session_state.mission = mission_choice
        st.rerun()

elif not st.session_state.submitted:
    st.subheader(f"🎯 미션: {st.session_state.mission}")
    st.caption(missions[st.session_state.mission])

    # 상품 목록 불러오기
    try:
        df = pd.read_excel("상품목록_이미지입력용.xlsx")
        products = []
        for i, row in df.iterrows():
            products.append({
                "id": f"item_{i}",
                "name": row["상품명"],
                "price": int(row["가격"]),
                "image": row["이미지_URL"] if pd.notna(row["이미지_URL"]) else None
            })
    except Exception as e:
        st.error(f"상품 목록을 불러오는 중 오류가 발생했습니다: {e}")
        st.stop()

    # 상품 선택
    st.subheader("2️⃣ 상품을 골라 담아보세요!")
    cols = st.columns(3)

    for i, item in enumerate(products):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown("""
                    <div style='height: 250px; display: flex; flex-direction: column; justify-content: space-between; align-items: center;'>
                        <div style='text-align: center; font-weight: bold;'>{name}</div>
                        <div style='margin: 5px 0;'>
                            <img src='{image}' style='width: 100px; height: 100px; object-fit: contain; display: block; margin: 0 auto;'>
                        </div>
                        <div style='text-align: center; font-size: 16px;'>💰 <strong>{price}원</strong></div>
                    </div>
                """.format(name=item['name'], image=item['image'], price=item['price']), unsafe_allow_html=True)

                qty = st.session_state.quantities.get(item["id"], 1)
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("➖", key=f"dec_{item['id']}") and qty > 1:
                        st.session_state.quantities[item["id"]] = qty - 1
                        st.rerun()
                with col2:
                    st.markdown(f"<div style='text-align: center;'>{qty}개</div>", unsafe_allow_html=True)
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
                            "image": item["image"]
                        }
                    with st.spinner(f"{item['name']} {qty}개 담았어요!"):
                        time.sleep(2)
                    st.rerun()

    # 장바구니 확인
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
                if item["image"]:
                    st.image(item["image"], width=50)
            with col2:
                st.markdown(f"**{item['name']}**  ")
                st.markdown(f"👉 **{item['qty']}개** × {item['price']}원  = 💰 **{subtotal}원**")
            with col3:
                if st.button("❌", key=f"remove_{pid}"):
                    del st.session_state.cart[pid]
                    st.rerun()

        st.markdown(f"### 🧾 총합: **{total} 원**")
        st.markdown(f"### 💰 잔액: **{BUDGET - total} 원**")

        if st.button("제출하고 결과 보기"):
            st.session_state.submitted = True
            st.rerun()

# 결과 확인 페이지
elif st.session_state.submitted:
    st.subheader("4️⃣ 결과 확인")
    total = sum(item["price"] * item["qty"] for item in st.session_state.cart.values())
    remaining = BUDGET - total

    st.success(f"총 {total}원을 사용했습니다.")
    st.info(f"잔액은 {remaining}원입니다.")

    st.markdown("## 🛍️ 내가 구매한 물품")
    for pid, item in st.session_state.cart.items():
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                if item["image"]:
                    st.image(item["image"], width=70)
            with col2:
                st.markdown(f"**{item['name']}** - {item['qty']}개 / 개당 {item['price']}원")

    st.markdown("---")
    st.markdown("### ✏️ 구매한 이유를 적어보세요:")
    reason = st.text_area("", placeholder="왜 이 물건들을 샀나요? 어떤 기준으로 선택했나요?", height=100)
    st.markdown("📝 이 결과를 보고 용돈기입장에 작성해보세요!")

    # 다운로드용 이미지 생성
    try:
        font = ImageFont.truetype("NanumHumanRegular.ttf", 20)
        item_height = 130
        width = 600
        height = item_height * len(st.session_state.cart)
        canvas = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(canvas)

        for i, item in enumerate(st.session_state.cart.values()):
            y_offset = i * item_height
            try:
                response = requests.get(item["image"], timeout=5)
                product_img = Image.open(BytesIO(response.content)).convert("RGBA").resize((100, 100))
                canvas.paste(product_img, (10, y_offset + 10))
            except:
                draw.text((10, y_offset + 40), "이미지 오류", fill="red", font=font)

            draw.text((120, y_offset + 10), item["name"], fill="black", font=font)
            draw.text((120, y_offset + 40), f"가격: {item['price']}원", fill="black", font=font)
            draw.text((120, y_offset + 70), f"수량: {item['qty']}개", fill="black", font=font)

        output = BytesIO()
        canvas.save(output, format="PNG")
        output.seek(0)
        st.download_button(
            label="📥 결과 이미지 다운로드",
            data=output,
            file_name="장바구니_결과.png",
            mime="image/png"
        )
    except Exception as e:
        st.warning(f"이미지 저장 중 오류 발생: {e}")

    st.warning("이전으로 돌아갈 수 없습니다. 다시 시작하려면 페이지를 새로고침 해주세요.")
