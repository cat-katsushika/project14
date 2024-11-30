import os

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def create_ai_comment(message):
    prompt = f"""
    以下のメッセージについて，
    英語以外の場合は英語に翻訳してください。
    英語の場合は日本語にに翻訳してください。
    また，翻訳した文章のみを返信してください。

    {message}
    """

    completion = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])

    return completion.choices[0].message.content
