class Customer:
    '고객데이터와 as_dic(), to_list_style(txt백업시), __str__()'
    def __init__(self, name, phone, email, age, grade, etc):
        self.name = name
        self.phone = phone
        self.email = email
        self.age  = age
        self.grade = grade
        self.etc = etc
    def as_dic(self):
        return {"name":self.name, 
                "phone":self.phone, 
                "email":self.email,
                "age":self.age, 
                "grade":self.grade, 
                "etc":self.etc}
    def to_list_style(self):
        # return "홍길동, 010-9999-9999, a@a.com, 30, 3, 까칠해"
#         return "{}, {}, {}, {}, {}, {}".format(self.name, self.phone, self.email,
#                                               self.age, self.grade, self.etc)
        temp = [self.name, 
                self.phone, 
                self.email, 
                str(self.age), 
                str(self.grade), 
                self.etc]
        return ', '.join(temp)
    def __str__(self):
        # return "  *** 홍길동, 010-9999-9999, a@a.com, 30, 까칠해"
        return "{:>5}\t{:3}\t{:13}\t{:15}\t{:3}\t{}".format('*'*self.grade,
                       self.name, self.phone, self.email, self.age, self.etc)
    

    def to_customer(row):
    # '''
    # row = "홍길동, 010-9999-9999, a@a.com, 30, 3, 까칠해"(txt파일 내용)을 매개변수로 받아
    # Customer 객체로 return 
    # '''
        data = row.split(',')
        name = data[0]
        phone = data[1].strip() # strip은 앞뒤 white space 제거
        email = data[2].strip()
        age = int(data[3].strip())
        grade = int(data[4].strip())
        etc = data[5].strip()
        return Customer(name, phone, email, age, grade, etc)


def load_customers():
    customer_list = []
    try:
        with open('data/ch09_customers.txt', 'r', encoding='utf-8') as f:
            # txt 데이터 한줄씩 customer 객체로 받아 customer_list.append
            lines = f.readlines()
            for line in lines:
                #line = "홍길동, 010-9999-9999, a@a.com, 30, 3, 까칠해"
                customer = to_customer(line)
                # print(customer)
                customer_list.append(customer)
    except:
        with open('data/ch09_customers.txt', 'w', encoding='utf-8') as f:
            print('초기화 파일을 생성했습니다')
    return customer_list


def fn1_insert_customer_info():
    '''
    사용자로부터 name, phone, email, age, grade, etc를 입력받아 Customer형 객체 반환
    '''
    import re
    name = input('이름 :')
    name_pattern = r'[가-힣]{2,}'
    
    while not re.search(name_pattern, name):
        print('이름을 제대로 입력하세요(한글 2글자 이상)')
        name = input('이름 :')
    
    phone = input('전화번호 :')
    email = input('이메일 :')

    while True:
        try:
            age = int(input('나이 :'))
            if (age < 0 or age > 130):
                raise Exception('나이 범위는 1살 ~ 129살입니다.')
            break
        except:
            print('올바른 나이를 입력하세요')
    
    try:
        grade = int(input('등급(1~5) :'))
        #grade = 1 if grade < 1 else 5 if grade > 5 else grade
        if grade < 1:
            grade = 1
        if grade > 5:
            grade = 5
    except:
        print('유효하지 않은 등급 입력시 1등급으로 초기화')
        grade = 1
    
    etc = (input('기타 :'))
    return Customer(name, phone, email, age, grade, etc)


def fn2_print_customers(customer_list):
    # 'customer_list를 출력(pdf 40page 스타일)'
    print('='*70)
    print('{:^70}'.format('고객 정보'))
    print('-'*70)
    print("{:>5}\t{:3}\t{:13}\t{:15}\t{:3}\t{}".format('GRADE','이름','전화','이메일','나이','기타'))

    print('='*70)
    for customer in customer_list:
        print(customer)
    print('='*70)


    def fn3_delete_customer(customer_list):
        delete_name = input('삭제할 고객 이름은? ')
        matched = [(idx, customer) for idx, customer in enumerate(customer_list) if customer.name == delete_name]
    
    if not matched:
        print(f'{delete_name}님 데이터가 존재하지 않습니다.')
        return

    print(f"\n[ {delete_name} 님으로 검색된 고객 목록 ]")
    for i, (idx, customer) in enumerate(matched):
        print(f'{i}: {customer}')  # i는 선택 번호, idx는 실제 인덱스

    while True:
        user_input = input('\n삭제할 번호를 입력하세요 (종료하려면 q): ')
        if user_input.lower() == 'q':
            print('삭제를 종료합니다.')
            break

        if not user_input.isdigit():
            print('숫자를 입력해주세요.')
            continue

        select = int(user_input)
        if 0 <= select < len(matched):
            del_idx = matched[select][0]
            print(f'{customer_list[del_idx].name} 고객 삭제됨.')
            del customer_list[del_idx]

            # 삭제 후 인덱스 갱신 필요
            matched = [(idx, customer) for idx, customer in enumerate(customer_list) if customer.name == delete_name]
            for i, (idx, customer) in enumerate(matched):
                print(f'{i}: {customer}')
            
            if not matched:
                print('더 이상 삭제할 고객이 없습니다.')
                break
        else:
            print('잘못된 번호입니다.')


            # 4. 이름찾기 (동명이인이 있음) 일부만 입력해도 검색가능
def fn4_search_customer(customer_list):
    # '''찾고자 하는 이름을 input으로 받아, customer_list에서 검색하여
    # 같은 이름은 search_list에 append한 후 search_list를 출력
    # 같은 이름이 없으면 없다고 출력'''
    search_name = input('이름은? ')
    found = [customer for customer in customer_list if search_name in customer.name]
    if found:
        fn2_print_customers(found)
    else:
        print(f'{search_name} 고객을 찾을 수 없습니다.')