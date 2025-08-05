from django.urls import path
from . import views

app_name = "wordcnt"

urlpatterns = [
    path("", views.wordinput, name="wordinput"),  # text를 입력하는 form태그 (POST전송 / GET차이)
    path("about/", views.about, name="about"),    # 도움말 페이지
    path("result/", views.result, name="result"), # 입력된 text의 글자수, 단어수, 각 단어 갯수 출력
]
