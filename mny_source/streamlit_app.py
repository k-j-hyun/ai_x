import streamlit as st

# 데이터
restaurants = [
    {"name": "김밥천국", "menu": "김밥", "price": 4000},
    {"name": "홍콩반점", "menu": "짬뽕", "price": 7500},
    {"name": "한솥도시락", "menu": "도시락", "price": 6000},
    {"name": "이차돌", "menu": "차돌박이", "price": 12000},
]

# UI
st.title("🍱 메뉴 추천기")

keyword = st.text_input("메뉴 키워드 입력 (예: 김밥, 도시락 등)")
price_range = st.selectbox("가격대 선택", ["low", "medium", "high"])

# 추천 함수
def recommend():
    def price_filter(r):
        if price_range == "low":
            return r["price"] <= 5000
        elif price_range == "medium":
            return 5000 < r["price"] <= 10000
        elif price_range == "high":
            return r["price"] > 10000
        return True

    result = [r for r in restaurants if keyword in r["menu"] and price_filter(r)]
    return result

if keyword:
    results = recommend()
    if results:
        for r in results:
            st.write(f"🍽️ {r['name']} - {r['menu']} ({r['price']}원)")
    else:
        st.warning("조건에 맞는 식당이 없어요!")

# 실행 streamlit run streamlit_app.py