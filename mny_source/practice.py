# 튜플을 리스트로 변환
my_tuple = ('서울','부산','목포')
my_list = list(my_tuple)
print(my_list)
# 출력: [1, 2, 3]

# 리스트를 딕셔너리로 변환
pair_list = [("a", 1), ("b", 2), ("c", 3)]
my_dict = dict(pair_list)
print(my_dict)
# 출력: {'a': 1, 'b': 2, 'c': 3}

# zip을 활용한 리스트 2개를 딕셔너리로 합치는 경우 key:value
keys = ["name", "age", "city"]
values = ["Alice", 25, "Seoul"]

my_dict = dict(zip(keys, values))
print(my_dict)  
# 출력: {'name': 'Alice', 'age': 25, 'city': 'Seoul'}

# 딕셔너리를 리스트로 변경 (key만 리스트로 바꾸기)
my_favorite = {'fruit': 'apple', 'number': 12, 'sport': 'golf'}
key_list = list(my_favorite.keys())
print(key_list)
# 출력 : ['fruit', 'number', 'sport']

# value만 리스트로 바꾸기
value_list = list(my_favorite.values())
print(value_list)
# 출력 : ['apple', 12, 'golf']

# key-value 쌍을 튜플로 묶어서 리스트로 변경
item_list = list(my_favorite.items())
print(item_list)
# 출력 : [('fruit', 'apple'), ('number', 12), ('sport', 'golf')]

# 딕셔너리를 하나의 리스트로 펼치는 방법
flat_list = []
for key, value in my_favorite.items():
    flat_list.append(key)
    flat_list.append(value)

print(flat_list)
# 출력 : ['fruit', 'apple', 'number', 12, 'sport', 'golf']