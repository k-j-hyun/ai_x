from django.db import models
import re
from django.forms import ValidationError
# Create your models here.

REGION_CHOICE = (
    ("Europe","유럽"),
    ("Asia", "아시아"),
    ("Oceania","오세아니아"),
    ("America","아메리카"),
)
def lnglat_validator(value):
    if not re.match(r'(\d+\.?\d*),(\d+\.?\d*)', value):
        raise ValidationError('Invalid LngLat. ex:38, 128')

class Post(models.Model): # blog_post 앱이름_클래스이름 테이블 생성
    # id = models.AutoField(primary_key=True) PK가 없을 경우 자동 생성
    title = models.CharField(verbose_name="제목", max_length=100,
                                help_text="기사 제목입니다. 100자 내외") # 최대 길이 반드시 지정(VARCHAR 타입)
    content = models.TextField("본문") # 최대길이 제한 없음 CLOB, TEXT 타입
    create_at = models.DateField(auto_now_add=True) # 자동 시간 생성
    update_at = models.DateTimeField(auto_now=True) # 자동 시간 수정
    region = models.CharField(verbose_name="지역",
                                max_length=20, choices=REGION_CHOICE,
                                default="Asia")
    lnglat = models.CharField(verbose_name="경,위도",
                                max_length=100,
                                blank=True,
                                null=True,
                                help_text="경도, 위도 포멧",
                                validators=[lnglat_validator])
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return "제목:{}-{}작성 {}최종 수정".format(self.title, self.create_at, self.update_at)
    class Meta:
        ordering = ['-update_at'] # 정렬 옵션
