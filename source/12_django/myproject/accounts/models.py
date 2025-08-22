from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
  user = models.OneToOneField(User,
          on_delete=models.CASCADE) # User가 삭제될 때, profile은 어떻게 할지?
  phone_number = models.CharField(verbose_name="전화", max_length=20)
  address      = models.CharField(verbose_name="주소", max_length=100)
  def __str__(self):
    return "{}({}-{})".format(self.user.username,
                              self.phone_number,
                              self.address)
  
  # 이벤트처리==signals사용 (post_save) : profile.save()성공시 가입인사를 메일 전송
from django.db.models.signals import post_save
from django.core.mail import send_mail

def on_send_mail(sender, **kwargs):
  print('★ on_send_mail :', kwargs)
  if kwargs['created']: # 회원가입 / False일 경우 회원정보 등 etc
    user = kwargs['instance'].user
    if not user.email: # 회원가입시 메일 입력 안함
      print('★ on_send_mail : user.email 없음')
      return
    # 이메일 전송
    subject = f"{user.username}님 사이트에 가입해 주셔서 감사합니다(메일제목)"
    body = f"안녕하세요 {user.username}님\n\n이메일 주소 : {user.email}\n\n환영합니다.(메일내용)"
    bodyHtml = f"<h1>안녕하세요 {user.username}님</h1><br><br>이메일 주소 : {user.email}<br><br><p>환영합니다.룰랄룰랄루 퉁퉁퉁퉁퉁퉁퉁퉁퉁 사후르!(메일내용)</p>"
    # settings.py에 EMAIL_BACKEND 설정
    from decouple import config
    send_mail(
      subject=subject,
      message=body,
      from_email=config('EMAIL_HOST_USER'),
      recipient_list=[user.email],
      html_message=bodyHtml,
      fail_silently=False, # 메일 전송이 안되었을 경우, 아무일도 하지 않음
    )


# on_send_mail 함수 -> post_save로 연결
post_save.connect(on_send_mail, sender=Profile)
