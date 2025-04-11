# crawler.py

import requests
from bs4 import BeautifulSoup

def crawl_naver_reviews(store_name):
    query = store_name + " 리뷰"
    url = f"https://search.naver.com/search.naver?query={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return ["리뷰를 가져오지 못했어요 😢"]

    soup = BeautifulSoup(res.text, "html.parser")
    
    # 검색결과에서 리뷰로 보이는 부분 긁어오기 (간단 예시)
    reviews = []
    for tag in soup.find_all("span"):
        txt = tag.get_text()
        if "맛있" in txt or "별점" in txt or "추천" in txt:
            reviews.append(txt)
        if len(reviews) >= 3:
            break

    if not reviews:
        return ["리뷰가 없어요 😅"]
    return reviews