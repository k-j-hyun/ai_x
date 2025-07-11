# 데코레이터 : 플라스크를 포함하여 다른 오픈소스 코드에 @로 시작하는 구문
# 대상함수를 감싸 함수 앞뒤 부가적인 구문을 추가해서 반복 작업을 수행

def check(func):
    def wrapper():
        print(func.__name__, '함수 전처리 작업함')
        func()
        print(func.__name__, '함수 후처리 작업함')
    return wrapper #function을 return

@check
def hello():
    print("Hello")

@check
def world():
    print("world")

if __name__ == "__main__":
    hello()
    world()