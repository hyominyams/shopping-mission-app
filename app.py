# 합리적 소비 장보기 미션 (Streamlit)
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import datetime, traceback

# ───────────────────────── 페이지·세션 설정 ─────────────────────────
st.set_page_config(page_title="합리적 소비 미션", layout="wide")
st.title("🏍️ 합리적 소비 장보기 미션")

BUDGET = 30_000   # 예산
if "mission" not in st.session_state:
    st.session_state.update(
        mission=None, cart={}, quantities={}, submitted=False,
        reason="", reason_submitted=False
    )

# ───────────────────────── 데이터 로드 ─────────────────────────
@st.cache_data
def load_products(path: str):
    df = pd.read_excel(path).dropna(subset=["상품명", "가격", "이미지_URL"])
    return [
        {"id": f"item_{i}", "name": r["상품명"], "price": int(r["가격"]), "image": r["이미지_URL"]}
        for i, r in df.iterrows()
    ]

products = load_products("상품목록_이미지입력용.xlsx")

missions = {
    "카레라이스 만들기 🍛": "카레에 필요한 재료를 선택해보세요!",
    "해외여행 준비 ✈️":   "여행 가기 전 필요한 물건을 준비하세요!",
    "소풍 도시락 준비 🎒": "소풍에 가져갈 도시락과 준비물을 선택하세요!"
}

# ───────────────────────── 1. 미션 선택 ─────────────────────────
if not st.session_state.mission and not st.session_state.submitted:
    st.subheader("1️⃣ 미션을 선택하세요")
    mission_choice = st.radio("미션 선택:", list(missions.keys()))
    if st.button("미션 시작하기"):
        st.session_state.mission = mission_choice
        st.experimental_rerun()

# ───────────────────────── 2. 상품 담기 화면 ─────────────────────────
elif not st.session_state.submitted:
    st.subheader(f"🎯 미션: {st.session_state.mission}")
    st.caption(missions[st.session_state.mission])

    st.subheader("2️⃣ 상품을 골라 담아보세요!")
    cols = st.columns(3)

    for i, item in enumerate(products):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{item['name']}**")
                st.image(item["image"], width=100)
                st.markdown(f"💰 **{item['price']}원**")

                # 수량 입력(NumberInput → rerun 최소화)
                qty_key = f"qty_{item['id']}"
                default_qty = st.session_state.quantities.get(item["id"], 1)
                qty = st.number_input(
                    "수량", min_value=1, value=default_qty, step=1, key=qty_key
                )
                st.session_state.quantities[item["id"]] = qty

                # 담기 버튼
                if st.button("🛒 담기", key=f"add_{item['id']}"):
                    cart = st.session_state.cart
                    if item["id"] in cart:
                        cart[item["id"]]["qty"] += qty
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
            with col1: st.image(it["image"], width=50)
            with col2:
                st.markdown(f"**{it['name']}**  \n👉 **{it['qty']}개** × {it['price']}원 = **{subtotal}원**")
            with col3:
                if st.button("❌", key=f"remove_{pid}"):
                    del cart[pid]; st.experimental_rerun()

        st.markdown(f"### 🧾 총합: **{total:,} 원**")
        st.markdown(f"### 💰 잔액: **{BUDGET - total:,} 원**")

        # 예산 초과 차단
        if total > BUDGET:
            st.error("예산을 초과했습니다! 장바구니를 조정해 주세요.")
        else:
            if st.button("제출하고 결과 보기"):
                st.session_state.submitted = True
                st.experimental_rerun()

# ───────────────────────── 4. 결과 확인 ─────────────────────────
elif st.session_state.submitted:
    cart = st.session_state.cart
    total = sum(it["price"] * it["qty"] for it in cart.values())
    remaining = BUDGET - total

    st.subheader("4️⃣ 결과 확인")
    st.success(f"총 {total:,}원을 사용했습니다.")
    st.info(f"잔액은 {remaining:,}원입니다.")

    st.markdown("## 🛍️ 내가 구매한 물품")
    for it in cart.values():
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1: st.image(it["image"], width=70)
            with col2: st.markdown(
                f"**{it['name']}** — {it['qty']}개 / 개당 {it['price']}원"
            )

    # 구매 이유 입력
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
            # 기본·제목 폰트
            font_path = "NanumHumanRegular.ttf"
            font = ImageFont.truetype(font_path, 18)
            title_font = ImageFont.truetype(font_path, 30)

            item_h, width = 130, 700
            height = item_h * (len(cart) + 4)
            canvas = Image.new("RGB", (width, height), "white")
            draw = ImageDraw.Draw(canvas)

            # ① 미션명(가운데·굵게)
            title = f"미션: {st.session_state.mission}"
            bbox = draw.textbbox((0, 0), title, font=title_font)
            draw.text(
                ((width - (bbox[2]-bbox[0])) // 2, 20),
                title, fill="black", font=title_font
            )

            # ② 품목 정보
            for idx, it in enumerate(cart.values(), start=1):
                y = 80 + (idx-1) * item_h
                # 이미지
                try:
                    img = Image.open(BytesIO(requests.get(it["image"], timeout=5).content)
                                     ).convert("RGBA").resize((100, 100))
                    canvas.paste(img, (20, y), img)
                except Exception:
                    draw.text((20, y+40), "이미지 오류", fill="red", font=font)

                # 텍스트
                text_y = y + 10
                draw.text((140, text_y), f"{it['name']}", fill="black", font=font)
                draw.text((140, text_y+35), f"수량: {it['qty']}개", fill="black", font=font)
                draw.text((140, text_y+65), f"가격: {it['price']}원", fill="black", font=font)

            # ③ 총액·이유
            y_summary = 80 + len(cart) * item_h
            draw.text((20, y_summary),     f"총 사용 금액: {total:,}원", fill="blue",  font=font)
            draw.text((20, y_summary+35), f"잔액: {remaining:,}원",   fill="green", font=font)
            draw.text((20, y_summary+70), f"이유: {st.session_state['reason']}", font=font, fill="black")

            # PNG 출력
            buf = BytesIO(); canvas.save(buf, format="PNG"); buf.seek(0)
            today = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{st.session_state.mission}_결과_{today}.png"

            st.download_button(
                "📄 결과 PNG 다운로드", buf, file_name=file_name, mime="image/png"
            )
        except Exception:
            st.error("이미지 생성 중 오류가 발생했습니다.")
            st.text(traceback.format_exc())

    # 처음으로 버튼 (세션 초기화)
    if st.button("🔄 처음으로"):
        st.session_state.clear()
        st.experimental_rerun()
