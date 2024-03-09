#Discord
import discord
from discord import app_commands as app_cmd
from discord.ext import commands as cmd
#Анализ html кода
from bs4 import BeautifulSoup as bs
#Селениум - Браузер
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#Функции системы
import os
import sys
#Оптимизация
import numpy as np
#Хранение
import json
#Полезная библиотека
import asyncio
#Математика
import math
#Оптимизация сообщений
from cogs.optimization.embeds import message_successfully_send

#---------------------------------------------
file_json = open('config.json', 'r')
data = json.load(file_json)

#---------------------------------------------
#Опции браузера
options = webdriver.FirefoxOptions()
options.add_argument("--enable-javascript")
options.add_argument("--start-maximized")
options.add_argument("--disable-extensions")
options.add_argument("--disable-popup-blocking")
#Чтоб браузер не было видно
os.environ['MOZ_HEADLESS'] = '1'
#Создание браузера
driver = webdriver.Firefox(options=options)
#Получение данных со страницы
driver.get('https://irinabot.ru/')
element = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "game-list-row"))
)

#---------------------------------------------

def getAllHostings(driver):
    #html-код получение
    main_page = driver.find_element(By.TAG_NAME, 'html')
    a = main_page.get_attribute('innerHTML')
    soup = bs(a, 'html.parser')
    #Нахождение игр
    allGames = soup.find_all('tr', 'game-list-row')
    
    #------------------------------------
    #Список игр
    gameList = []
    for game in allGames:
        #Список информации о игре: [Версия, Кол-во игроков, Название, Игроки, Владелец]
        gameData = []
        for element in game:
            gameData.append(element.text)
        #Лист игроков
        playerList = []
        for el2 in game.find_all('div', 'ui'):
            for el3 in el2:
                playerList.append(el3.find('span').text)
        #Добавление в массив игр
        gameList.append([gameData[0], gameData[1], gameData[2], playerList])
    #Возращение массива игр
    return gameList

#----------------

def dsEmbed(driver):
    #Получение данных о хостингах
    allHostings = getAllHostings(driver=driver)
    allHostings_len = len(allHostings)
    #Преобразование в массив discord.Embed
    embeds = np.array([], dtype=discord.Embed)
    start_embed = discord.Embed(title="Хостинги на Irina Host Bot", 
                                description=f"Ниже находится список всех хостингов, которые есть на сайте [Irina Host Bot](https://irinabot.ru/)",
                                color=discord.Color.from_str("#1971ff"))
    embeds = np.append(embeds, start_embed)
    for i in range(math.ceil(allHostings_len/25)):
        #Создание временного discord.Embed
        cash_embed = discord.Embed(color=discord.Color.from_str("#1971ff"))
        #Добавление списка игроков
        for j in range(25*i, min(25*(i+1),allHostings_len)):
            players: str = "Игроки: "
            if allHostings[j][3] == []:
                players = "ㅤ"
            else:
                for player in allHostings[j][3]:
                    players += f"`{player}` "
            #Создание поля в embed с игрой
            cash_embed.add_field(name=f"{allHostings[j][0]} | {allHostings[j][1]}\n{allHostings[j][2]}",
                                value=players, 
                                inline=True)
        #Расширения массива embed'ov на наш временный
        embeds = np.append(embeds, cash_embed)
    #Возращение всех embed'ov
    return embeds
            
            
            

#---------------------------------------------
class irinabothostings(cmd.Cog):
    #Получение бота в нашу среду self
    def __init__(self, bot):
        self.bot = bot
    
    #Отслеживаем запуск. cmd.Cog.listener() = bot.event (Только первое используется в cog'ах, а второе основном скрипте с ботом)
    @cmd.Cog.listener()
    async def on_ready(self):
        #Проверка: есть ли вообще сообщение которое мы будем менять
        while True:
            if data[0]["Parser"]["ChannelID"] == "" or data[0]["Parser"]["MessageID"] == "":
                await asyncio.sleep(60)
            else:
                break
        
        #Получение канала и сообщения
        channel:discord.TextChannel = self.bot.get_channel(data[0]["Parser"]["ChannelID"])
        message:discord.Message = await channel.fetch_message(data[0]["Parser"]["MessageID"])
        
        #Постоянное обновление
        while True:
            embs = dsEmbed(driver)
            await message.edit(embeds=embs)
            await asyncio.sleep(30)
    
    #----------------------------------------
    
    #Команда для отправки сообщения, которое будет выводить хостинги
    @app_cmd.command(name="сообщение-для-хостов", description="Сообщение для парсера хостингов")
    @app_cmd.describe(channel_to_post = "Канал в который будет отправлено сообщение")
    @app_cmd.default_permissions(administrator = True)
    async def host_message(self, interaction: discord.Interaction, channel_to_post: discord.TextChannel):
        #Пишем сообщение, которое будет меняться
        message: discord.Message = await channel_to_post.send(content="Сообщение для парсера.")
        
        #Меняем значение в config.json
        data[0]["Parser"]["ChannelID"] = channel_to_post.id
        data[0]["Parser"]["MessageID"] = message.id
        #Изменяем файл
        with open('config.json', 'w', encoding ='utf8') as json_file: 
            json.dump(data, json_file, indent=4) 
        #Отвечаем пользователю
        await interaction.response.send_message(embed = message_successfully_send(), ephemeral=True)
        

    #------------------------------------------------------
    
    #Команда чтобы закрывать бота и браузер (во избежание ошибок) 
    @app_cmd.command(name="закрыть-бота")
    async def shutup(self, interaction: discord.Interaction):
        if interaction.user.id == 1064888272393875527:
            driver.close()
            await interaction.response.send_message("Бот закрывается")
            sys.exit()
        else:
            await interaction.response.send_message("Вы не владелец бота")
        
async def setup(bot):
    await bot.add_cog(irinabothostings(bot))
        