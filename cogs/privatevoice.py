#Discord
import discord
from discord import app_commands as app_cmd
from discord.ext import commands as cmd
from discord import ui, ButtonStyle
from discord.utils import MISSING
#Оптимизация
import numpy as np
#Хранение
import json
#Полезная библиотека
import asyncio
from datetime import datetime as dt
#Базы данных
import sqlite3
#Оптимизация сообщений
from cogs.optimization.embeds import message_successfully_send

#----------------------------------------------------------------------
file_json = open('config.json', 'r')
data = json.load(file_json)

#----------------------------------------------------------------------

connection = sqlite3.connect('Database.db')
cursor = connection.cursor()

#----------------------------------------------------------------------

class PrivateVoiceModal(discord.ui.Modal):
    def __init__(self, *, title: str,modal_def) -> None:
        super().__init__(title=title, timeout=None)
        self.modal_def = modal_def
    
    parameter = discord.ui.TextInput(label="Значение",placeholder='Введите сюда')
    async def on_submit(self, interaction: discord.Interaction):
        await self.modal_def(interaction, self.parameter.value)

class PrivateVoiceButton(discord.ui.Button):
    def __init__(self, custom_id: str, custom_id_add:str, emoji: str, modal_title: str, modal_def):
        super().__init__(style=ButtonStyle.grey, custom_id=f"{custom_id}:{custom_id_add}:button", emoji=emoji)
        self.modal_title = modal_title
        self.modal_def = modal_def
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(PrivateVoiceModal(title=self.modal_title, modal_def=self.modal_def))

class PrivateVoiceView(discord.ui.View):
    def __init__(self, custom_id, guild: discord.Guild):
        super().__init__(timeout=None)
        self.add_item(PrivateVoiceButton(custom_id=custom_id, custom_id_add="name", emoji=guild.get_emoji(985583494174486539),
                                         modal_title="Изменение названия канала", modal_def=channel_name))
        self.add_item(PrivateVoiceButton(custom_id=custom_id, custom_id_add="limit", emoji=guild.get_emoji(985583500650487808),
                                         modal_title="Изменение лимита канала", modal_def=channel_limit))

def sqliteUpdate(column: str, member_id:int, value):
    if isinstance(value, str):
        cursor.execute(f"UPDATE PrivateVoice SET {column} = '{value}' WHERE member_id = {member_id}")
        connection.commit()
    elif isinstance(value, int):
        cursor.execute(f"UPDATE PrivateVoice SET {column} = {value} WHERE member_id = {member_id}")
        connection.commit()


standart_response = discord.Embed(title="Сообщение успешно отправлено", color = discord.Color.from_str("#0dde2d"), timestamp=dt.utcnow())
bad_response = discord.Embed(title="Вам нужно ввести число", color = discord.Color.from_rgb(255,0,0), timestamp=dt.utcnow())
async def channel_name(inter: discord.Interaction, newParameter:str):
    sqliteUpdate(column='name', member_id=inter.user.id, value = newParameter)
    await inter.channel.edit(name=newParameter)
    await inter.response.send_message(embed = standart_response, ephemeral=True)
    
async def channel_limit(inter: discord.Interaction, newParameter:str):
    if newParameter.isdigit():
        sqliteUpdate(column='voice_limit', member_id=inter.user.id, value = int(newParameter))
        await inter.channel.edit(user_limit=int(newParameter))
        await inter.response.send_message(embed = standart_response, ephemeral=True)
    else:
        await inter.response.send_message(embed = bad_response, ephemeral=True)

#----------------------------------------------------------------------
class privatevoice(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    #before = None - если только зашёл в канал; after = None - если игроков вышел с голосового канала
    @cmd.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before, after):
        if after.channel is not None:
            if after.channel.id == data[0]["PrivateVoice"]["privatevoice_channel_id"]:
                private_voice_category_channel = member.guild.get_channel(data[0]["PrivateVoice"]["privatevoice_category_id"])
                private_voice_name = cursor.execute(f"SELECT name FROM PrivateVoice WHERE member_id = {member.id}").fetchone()[0]
                private_voice_limit = cursor.execute(f"SELECT voice_limit FROM PrivateVoice WHERE member_id = {member.id}").fetchone()[0]
                private_voice_bitrate = cursor.execute(f"SELECT bitrate FROM PrivateVoice WHERE member_id = {member.id}").fetchone()[0]*1000
                
                private_voice_overwrites = {
                    member.guild.default_role: discord.PermissionOverwrite(view_channel=True, read_message_history = True, speak = True, connect = True, use_voice_activation = True)
                }
                
                private_voice = await member.guild.create_voice_channel(name=private_voice_name,
                                                                        bitrate=private_voice_bitrate,
                                                                        user_limit=private_voice_limit,
                                                                        category = private_voice_category_channel,
                                                                        overwrites=private_voice_overwrites)
                await member.move_to(private_voice)
                
                await private_voice.send(embed=discord.Embed(title="Редактирование голосового канала", colour=discord.Color.from_str("#e310c0")), view = PrivateVoiceView(private_voice.id, member.guild))
        
        if before.channel is not None:
            if before.channel in member.guild.get_channel(data[0]["PrivateVoice"]["privatevoice_category_id"]).channels and before.channel.id != data[0]["PrivateVoice"]["privatevoice_channel_id"]:
                if len(before.channel.members) == 0:
                    await before.channel.delete()
        

                

async def setup(bot):
    await bot.add_cog(privatevoice(bot))