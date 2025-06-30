# 자동 완성이 안 될 경우(가상환경 설정이 안 되어있는 경우) : ctrl+shift+p->가상환경설정

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import os
import warnings
import time

warnings.filterwarnings("ignore")

# 1. client 생성
load_dotenv(".env", override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. assistant 생성 (assistant.id필요)
assistant_cs = client.beta.assistants.create(
    name="CustomerSupportBot",
    instructions="당신은 고객 지원 챗봇입니다. 사용자 문의에 대해 30자 이내로 친절한 답변을 하세요.",
    model="gpt-4o-mini",
#     tools=[]
)

# 3. thread 생성 : 기억 담당
thread_cs = client.beta.threads.create()
print('챗봇이 시작됩니다.(종료:종료, exit, q 입력) 모든 대화 이력은 저장됩니다.')

# while True 4, 5, 6
'''thread에 user 메시지(프롬프트) 추가
run 수행 (assistant.id, thread.id필요)
최종 assistant 답변 출력'''
while True:
    user_input = input("User : ").strip()
    if user_input.lower() in ('종료', 'exit', 'q'):
        print('챗봇이 종료됩니다. 이용해주셔서 감사합니다.')
        break
    if user_input == '':
        continue
    # 4,5,6 : user_input을 thread_cs에 추가하고 실행한후 최종 답변 출력
    ' 4. thread에 user_input을 추가 '
    client.beta.threads.messages.create(
        thread_id=thread_cs.id,
        role="user",
        content=user_input
    )
    ' 5. run(실행) '
    client.beta.threads.runs.create_and_poll(
        thread_id=thread_cs.id,
        assistant_id=assistant_cs.id
    )
    ' 6. 최종 답변 출력 '
    messages = client.beta.threads.messages.list(thread_id=thread_cs.id)
    assistant_reply = messages.data[0] # 최신답변
    reply_text = assistant_reply.content[0].text.value
    # print(f"user : {user_input}")
    print(f"assistant : {reply_text}")

# 7. 대화 이력 뽑아, 파일 출력
sorted_messages = sorted(messages.data, key=lambda msg : msg.created_at)
with open('data/ch7_chat_history.txt', 'w', encoding='utf-8') as f:
    for message in sorted_messages:
        # 생성 시각(message.created_at)을 datetime으로 변환
        datetime_info = time.localtime(message.created_at)
        output_str = time.strftime("%Y-%m-%d %H:%M:%S", datetime_info)
        # 파일 출력
        f.write("{:9}({}) : {}\n".format(message.role, output_str, message.content[0].text.value))