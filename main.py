import discord # Подключаем библиотеки
from discord.ext import commands
import os
import json
import asyncio
import sqlite3

#------------------------------------------
#Таблицы, json
data = json.load(open('config.json', 'r'))

#----------------------------------------
connection = sqlite3.connect('Database.db')
cursor = connection.cursor()
#Таблица для приваток
cursor.execute('''CREATE TABLE IF NOT EXISTS PrivateVoice(member_id INTEGER, name TEXT, voice_limit INTEGER, bitrate INTEGER)''')
#----------------------------------------

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix=data[0]['Bot']['prefix'], intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    
    for guild in bot.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT member_id FROM PrivateVoice WHERE member_id = {member.id}").fetchone() is None:
                cursor.execute(f'INSERT INTO PrivateVoice (member_id, name, voice_limit, bitrate) VALUES ({member.id}, "Приватка {member.name}", 0, 64)')
    connection.commit()

    print(f"Бот запущен: {bot.user.name}\nПинг бота: {round(bot.latency*1000)} мс")


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f'cogs.{filename[:-3]}')
    
asyncio.run(load())
bot.run(data[0]['Bot']['token'])