import os

import discord
import requests

from get_ai_message import create_ai_comment
from webhook import WEBHOOK_URLS

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # メンバーの状態変更を受け取るために必要

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))
    channel = client.get_channel(channel_id)
    if channel is None:
        print("チャンネルが見つかりません。DISCORD_CHANNEL_IDを確認してください。")
    else:
        await channel.send(f"準備OKだよ!")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    message_content = message.content
    channel_id = message.channel.id

    if len(message_content) >= 2000:
        await message.channel.send(f"メッセージが長いため翻訳を諦めました!\n文字数: {len(message_content)} \n{message_content}")
        return

    text = create_ai_comment(message_content)

    webhook_url = WEBHOOK_URLS[str(channel_id)]
    if webhook_url is None:
        print("Webhook URLが見つかりません。")
        return
    
    username = message.author.display_name
    avatar_url = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url

    send_webhook_reply(webhook_url, text, username, avatar_url)
    


@client.event
async def on_raw_reaction_add(payload):

    """
    リアクションの追加イベント
    """
    # リアクションを押したユーザーがボットの場合は無視
    if payload.member.bot:
        return

    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    message_content = message.content
    reaction_emoji = payload.emoji.name
    print(payload.channel_id)

    text = create_ai_comment(message_content, reaction_emoji)

    webhook_url = WEBHOOK_URLS[str(payload.channel_id)]
    if webhook_url is None:
        print("Webhook URLが見つかりません。")
        return

    username = payload.member.display_name
    avatar_url = payload.member.avatar.url if payload.member.avatar else payload.member.default_avatar.url

    # Webhookでメッセージ送信
    send_webhook_reply(webhook_url, text, username, avatar_url)


def send_webhook_reply(webhook_url, message, username, avatar_url):
    data = {
        "content": message,
        "username": username,
        "avatar_url": avatar_url,
    }
    requests.post(webhook_url, data=data, timeout=10)

client.run(os.getenv("DISCORD_TOKEN"))
