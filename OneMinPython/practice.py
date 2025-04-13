# lang = 'PYTHON'  
# print(lang[0])
# print(lang[1:6])
# today = '일요일'
# if today == '화화요일':
#     print('게임한판')
# else:
#     print('게임안함')
# print('공부시작')

# for n in range(1,31,10):
#     print(f'{n}번은 {n}번부터 {n+9}번까지 모아줘')
# def print_hello():
#     print('hello')
#     return 'hello'

# print_hello()
def order(shot=2, size='Regular', takeout=True):
    print(f'주문하신 음료는 {shot}샷, {size}사이즈, 포장여부는 {takeout}입니다.')

if takeout:
    print('포장 주문이 완료되었습니다.')
else:
    print('매장 주문이 완료되었습니다.')

order(3, 'Large', False)
order(2, 'Regular', True)