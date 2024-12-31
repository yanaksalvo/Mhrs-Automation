from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon import functions, types
from telethon.tl.custom import Button
from telethon.tl.functions.channels import JoinChannelRequest

from datetime import datetime
import random
import os
import time
import threading
import asyncio
import sys
import nest_asyncio
import json

class TelegramMessage:
    def __init__(self, sendTimeStamp, userId, contentText, platform):
        self.sendTimeStamp = sendTimeStamp
        self.userId = userId
        self.contentText = contentText
        self.platform = platform

        nest_asyncio.apply()

        if sys.platform:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Telegram:
    def __init__(self, api_id, api_hash, bot_token):
        self.currentPath = os.path.dirname(__file__)
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = None if len(bot_token) == 0 else bot_token

    async def login(self):
        api_id = self.api_id
        api_hash = self.api_hash
        bot_token = self.bot_token

        sessionFolder = f"{self.currentPath}\\sessions\\{api_hash}"
        
        if os.path.isdir(sessionFolder) == False:
            os.mkdir(sessionFolder) 
        
        self.client = TelegramClient(f"{sessionFolder}\\", api_id, api_hash)
        await self.client.start(bot_token=bot_token)

        return self.client
        
    async def send_message(self, chatId, messageContent):
        await self.client.send_message(chatId, messageContent, parse_mode="HTML")
    
    