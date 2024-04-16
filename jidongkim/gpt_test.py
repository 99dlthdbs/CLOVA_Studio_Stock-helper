from openai import OpenAI

client = OpenAI(api_key="")

stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "C에서 숫자 배열을 빠르게 정렬하는 코드를 작성해줘"}],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
