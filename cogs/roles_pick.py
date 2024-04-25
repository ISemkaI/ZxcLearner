#Discord
from typing import List
import discord
from discord import app_commands as app_cmd
from discord import TextStyle, ButtonStyle
from discord.ext import commands as cmd
from discord.ui import View, Button, Modal, Select
#Функции системы
import os
import sys
#Оптимизация
from discord.utils import MISSING
import numpy as np
#Хранение
import json
from datetime import datetime as dt
#Полезная библиотека
import asyncio
import sqlite3

#--------------------------------------------------------------
#Sqlite connect

connection = sqlite3.connect('Database.db')
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS PickRolesButtonsId(channel_id INTEGER, button_id TEXT, roleslist TEXT, guild_id INTEGER)''')

#--------------------------------------------------------------

pick_roles_emb_games = discord.Embed(title="Выбор игровых ролей",
                                     description=f"В зависимости от того, какие игры вы выберете, те каналы у вас и откроются.\n`Выбрать можно несколько ролей, либо с помощью специальных кнопок взять все или все убрать.`",
                                     colour=discord.Color.from_rgb(46, 219, 133))

pick_role_user = discord.Embed(title="Обновление ролей", colour = discord.Color.green()).set_footer(text="Если у вас была роль - она удаляется, если не было, добавляется")

succesful_send = discord.Embed(title="Сообщение было успешно отправлено", colour=discord.Color.green())
roles_add = discord.Embed(title="Все роли были успешно взяты", colour=discord.Color.green())
roles_del = discord.Embed(title="Все роли были успешно удалены", colour=discord.Color.green())

#--------------------------------------------------------------

class pickRolesSelect(Select):
    def __init__(self, custom_id: str, placeholder: str, options):
        super().__init__(custom_id=custom_id, placeholder=placeholder, min_values=0, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        cash_emb = pick_role_user
        descrip = ""
        guild = interaction.guild
        user = interaction.user
        user_roles = interaction.user.roles
        if self.values != []:
            await interaction.response.defer()
            for roleID in self.values:
                role = guild.get_role(int(roleID))
                if role not in user_roles:
                    await user.add_roles(role)
                    descrip+=f"\n> `Была добавлена роль` {role.name}"
                else:
                    await user.remove_roles(role)
                    descrip+=f"\n> `Была удалена роль` {role.name}"
            cash_emb.description = descrip
            cash_emb.timestamp = dt.now()
            await interaction.followup.send(embed=cash_emb, ephemeral=True)
        else:
            cash_emb.description = "Изменений нету"
            cash_emb.timestamp = dt.now()
            await interaction.response.send_message(embed=cash_emb, ephemeral=True)
            
            
class pickAllRoles(Button):
    def __init__(self, custom_id: str, listRoles: List[discord.Role]):
        super().__init__(style=ButtonStyle.green, label="Взять все роли", custom_id=custom_id)
        self.roles_list = listRoles
        
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_roles = interaction.user.roles
        for role in self.roles_list:
            if role not in user_roles:
                await interaction.user.add_roles(role)
        await interaction.followup.send(embed=roles_add, ephemeral=True)
        
class delAllRoles(Button):
    def __init__(self, custom_id: str, listRoles: List[discord.Role]):
        super().__init__(style=ButtonStyle.red, label="Убрать все роли", custom_id=custom_id)
        self.roles_list = listRoles
        
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_roles = interaction.user.roles
        for role in self.roles_list:
            if role in user_roles:
                await interaction.user.remove_roles(role)
        await interaction.followup.send(embed=roles_del, ephemeral=True)
        

                

        
        


class pickRolesView(discord.ui.View):
    def __init__(self, cs_id: str, rolesList: List[discord.Role]):
        super().__init__(timeout=None)
        self.add_item(pickRolesSelect(custom_id = f"{cs_id}:select", 
                                      placeholder="Выберите игровые роли",
                                      options=[discord.SelectOption(label=f"{rolesList[i].name}", value=rolesList[i].id) for i in range(len(rolesList))]))
        self.add_item(pickAllRoles(custom_id=f"{cs_id}:pickall", listRoles=rolesList))
        self.add_item(delAllRoles(custom_id=f"{cs_id}:delall", listRoles=rolesList))

#--------------------------------------------------------------
#Меню ролей, которые смогут выбрать пользователи

class sendSelect(discord.ui.RoleSelect):
    def __init__(self, *, placeholder: str, min_values: int, max_values: int, chan: discord.TextChannel):
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values)
        self.channel_send = chan
        
    async def callback(self, interaction: discord.Interaction):
        cs_id = f"{self.channel_send.id}:{interaction.guild.id}:{dt.now()}"
        await self.channel_send.send(embed=pick_roles_emb_games, view = pickRolesView(cs_id=cs_id, rolesList=self.values))
        cursor.execute(f'INSERT INTO PickRolesButtonsId(channel_id, button_id, roleslist, guild_id) VALUES ({self.channel_send.id}, "{cs_id}", "{[x.id for x in self.values]}", {interaction.guild.id})')
        connection.commit()
        await interaction.response.send_message(embed=succesful_send,ephemeral=True)

class sendView(View):
    def __init__(self, channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.add_item(sendSelect(placeholder="Выберите роли, которые смогут получить пользователи",
                                 min_values=1, max_values=15, chan=channel))

#--------------------------------------------------------------

class roles_pick(cmd.Cog):
    #Получение бота в нашу среду self
    def __init__(self, bot):
        self.bot = bot
        """except Exception:
            cursor.execute(f'DELETE FROM PickRolesButtonsId WHERE channel_id = {el[0]}')
            connection.commit()"""
    
    
    @cmd.Cog.listener()
    async def on_ready(self):
        data = cursor.execute("SELECT * FROM PickRolesButtonsId").fetchall()
        for el in data:
            guild = self.bot.get_guild(el[3])
            self.bot.add_view(pickRolesView(cs_id=el[1], rolesList=[guild.get_role(z) for z in eval(el[2])]))
    #Команда для отправки сообщения, которое будет выводить хостинги
    @app_cmd.command(name="получение-ролей", description="Сообщение для выбора ролей")
    @app_cmd.describe(channel_to_send = "Канал в который будет отправлено сообщение")
    @app_cmd.default_permissions(administrator = True)
    async def pick_roles(self, interaction: discord.Interaction, channel_to_send: discord.TextChannel):
        await interaction.response.defer()
        await interaction.followup.send(embed = discord.Embed(title = "Выберите роли").\
            set_author(name=interaction.guild.name, icon_url=interaction.guild.icon), 
                                                          view = sendView(channel=channel_to_send))        
        
async def setup(bot):
    await bot.add_cog(roles_pick(bot))