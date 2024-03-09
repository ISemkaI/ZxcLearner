#Discord
import discord
from discord import app_commands as app_cmd
from discord.ext import commands as cmd
from discord import ui, ButtonStyle
#Оптимизация
import numpy as np
#Хранение
import json
#Полезная библиотека
import asyncio
#Базы данных
import sqlite3
#Оптимизация сообщений
from cogs.optimization.embeds import message_successfully_send

#----------------------------------------------------------------------
file_json = open('config.json', 'r')
data = json.load(file_json)

#----------------------------------------------------------------------
class PrivateVoiceButton(discord.ui.Button):
    def __init__(self, custom_id: str, emoji: str):
        super().__init__(style=ButtonStyle.grey, custom_id=custom_id, emoji=emoji)

class PrivateVoiceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
        

#----------------------------------------------------------------------
class additional_commands(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_cmd.command(name = "аватар", description="Команда для получения id и названия эмодзи")
    @app_cmd.describe(member = "Участник в дискоре, если не указать будете вы")
    async def emoji_getter(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            await interaction.response.send_message(embed = discord.Embed(title = f"Аватар: {interaction.user.name}").set_image(url = interaction.user.avatar))
        else:
            await interaction.response.send_message(embed = discord.Embed(title = f"Аватар: {member.name}").set_image(url = member.avatar))
                
async def setup(bot):
    await bot.add_cog(additional_commands(bot))
