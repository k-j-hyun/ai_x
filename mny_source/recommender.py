# recommender.py

recent_recommendations = []  # 임시로 최근 추천 저장 (DB 쓰면 더 좋음)

def recommend_restaurants(keyword, price_range, exclude_recent=True):
    # 예시 식당 목록
    sample_restaurants = [
        {"name": "김밥천국", "menu": "김밥", "price": 4000},
        {"name": "홍콩반점", "menu": "짬뽕", "price": 7500},
        {"name": "한솥도시락", "menu": "도시락", "price": 6000},
        {"name": "이차돌", "menu": "차돌박이", "price": 12000},
    ]

    # 가격대 필터
    def price_filter(r):
        if price_range == "low":
            return r["price"] <= 5000
        elif price_range == "medium":
            return 5000 < r["price"] <= 10000
        elif price_range == "high":
            return r["price"] > 10000
        return True

    # 키워드 & 가격 필터링
    result = [
        r for r in sample_restaurants
        if keyword in r["menu"] and price_filter(r)
    ]

    # 최근 추천 제외
    if exclude_recent:
        result = [r for r in result if r["name"] not in recent_recommendations]

    # 추천한 가게 저장
    recent_recommendations.extend([r["name"] for r in result])

    return result

# test
if __name__ == "__main__":
    keyword = "도시락"
    price_range = "medium"

    results = recommend_restaurants(keyword, price_range)

    for r in results:
        print(f"🍱 {r['name']} - 메뉴: {r['menu']}, 가격: {r['price']}원")