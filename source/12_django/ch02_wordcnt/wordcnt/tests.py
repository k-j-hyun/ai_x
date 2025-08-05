from django.test import TestCase

# Create your tests here.
fulltxt = "홍길동 홍길동 아자"
strlengrth = len(fulltxt)        # 글자수
words = fulltxt.split()          # 단어들
wordcnt = len(fulltxt.split())   # 단어수
words_dic = dict()               # 빈 딕셔너리 => {'홍길동': 2, '아자': 1}
for word in words:
    if word in words_dic.keys():
        words_dic[word] += 1
    else:
        words_dic[word] = 1

print(fulltxt)
print("글자수 : ", strlengrth)
print("단어들 : ", words)
print("단어수 : ", wordcnt)
print("출현단어(리스트) : ", words_dic.items()) # 딕셔너리를 리스트로 출력
