#Discord
from typing import List
import discord
from discord import app_commands as app_cmd
from discord.ext import commands as cmd
from discord import ui, ButtonStyle
#Оптимизация
from discord.utils import MISSING
import numpy as np
#Хранение
import json
#Полезная библиотека
import asyncio
from datetime import datetime as dt
#Базы данных
import sqlite3

#----------------------------------------------------------------------
#json load

file_json = open('config.json', 'r')
data = json.load(file_json)

#----------------------------------------------------------------------
#Sqlite connect

connection = sqlite3.connect('Database.db')
cursor = connection.cursor()

#----------------------------------------------------------------------
#Проверка на владельца

def in_private_voice(interact: discord.Interaction):
    pr_channel = interact.user.voice.channel
    if pr_channel is not None:
        if pr_channel in interact.guild.get_channel(data[0]["PrivateVoice"]["privatevoice_category_id"]).channels and\
            pr_channel != interact.guild.get_channel(data[0]["PrivateVoice"]["privatevoice_channel_id"]):
                    return True
        else: return False
    else: return False

#----------------------------------------------------------------------
#Шаблоны

def ready_embeds(embed_name:str, iter: discord.Interaction):
    if embed_name == "not_in_voice":
        return userInteractionEmbed(interactionUser=iter, 
                                    title="Ошибка приватных голосовых каналов", descript="Вы не находитесь в приватном голосовом канале")
    elif embed_name == "not_owner":
        return userInteractionEmbed(interactionUser=iter, 
                                    title="Ошибка приватных голосовых каналов", descript="Вы не являетесь владельцем приватного голосового канала")
        

#----------------------------------------------------------------------
#Стандартизированный ответ
    
def userInteractionEmbed(interactionUser: discord.Interaction, title: str, descript: str):
    cashe_emb = discord.Embed(
        title=title, description=f"{interactionUser.user.mention}, {descript}",
        colour=discord.Color.from_str("#2b2d31"),
        timestamp=dt.now(),
    ).set_thumbnail(url=interactionUser.user.avatar)
    
    return cashe_emb

#----------------------------------------------------------------------
#Стандартизированные классы

#Меню с вводом данных
class PrivateVoiceModal(discord.ui.Modal):
    def __init__(self, *, title: str,modal_def) -> None:
        super().__init__(title=title, timeout=None)
        self.modal_def = modal_def
    
    parameter = discord.ui.TextInput(label="Значение",placeholder='Введите сюда')
    async def on_submit(self, interaction: discord.Interaction):
        await self.modal_def(interaction, self.parameter.value)

#Кнопка приватных голосовых каналов
class PrivateVoiceButton(discord.ui.Button):
    def __init__(self, custom_id: str, custom_id_add:str, emoji: str, row: int, modal_def, need_modal: bool, labBut: str, modal_title: str = None):
        super().__init__(style=ButtonStyle.grey, custom_id=f"{custom_id}:{custom_id_add}:button", emoji=emoji, label=labBut,row=row)
        self.modal_title = modal_title
        self.modal_def = modal_def
        self.need_modal = need_modal
    
    async def callback(self, interaction: discord.Interaction):
        user_chan = interaction.user.voice.channel
        if in_private_voice(interact=interaction):
                if interaction.user.id == cursor.execute(f"SELECT owner_id FROM PrivateVoiceOwner WHERE channel_id = {user_chan.id}").fetchone()[0]:
                    if self.need_modal:
                        await interaction.response.send_modal(PrivateVoiceModal(title=self.modal_title, modal_def=self.modal_def))
                        
                    else:
                        await self.modal_def(interaction)    
                        
                else:
                    if self.modal_def.__name__ == "take_owner":
                        await self.modal_def(interaction)
                        
                    else:
                        await interaction.response.send_message(embed=ready_embeds(iter=interaction, embed_name="not_owner"), ephemeral=True)  
        else:
            await interaction.response.send_message(embed=ready_embeds(iter=interaction, embed_name="not_in_voice"), ephemeral=True) 
#----------------------------------------------------------------------
#View кнопок

class PrivateVoiceView(discord.ui.View):
    def __init__(self, custom_id, bot):
        super().__init__(timeout=None)
        guild = bot.get_guild(956118594855501844)
        self.add_item(PrivateVoiceButton(custom_id=custom_id, custom_id_add="name", row=1,emoji=guild.get_emoji(1216293018114719855),
                                         modal_title="Изменение названия канала", modal_def=channel_name, need_modal=True, labBut="Название"))
        self.add_item(PrivateVoiceButton(custom_id=custom_id, custom_id_add="owner_get", row=1, emoji=guild.get_emoji(1231620349964058635),
                                         labBut="Забрать права", modal_def=take_owner, need_modal=False))
        self.add_item(PrivateVoiceButton(custom_id=custom_id, custom_id_add="security", row=1, emoji=guild.get_emoji(1216290035125452820),
                                         labBut="Приватность", modal_def=private_settings, need_modal=False))
        self.add_item(PrivateVoiceButton(custom_id=custom_id, custom_id_add="limit", row=2, emoji=guild.get_emoji(1216293036515004566),
                                         modal_title="Изменение лимита канала", modal_def=channel_limit, need_modal=True, labBut="Лимит"))
        self.add_item(PrivateVoiceButton(custom_id=custom_id, custom_id_add="owner_give", row=2, emoji=guild.get_emoji(1231621677952012499),
                                         labBut="Передать права", modal_def=give_owner, need_modal=False))
        self.add_item(PrivateVoiceButton(custom_id=custom_id, custom_id_add="member_ban", row=2, emoji=guild.get_emoji(1216275380856426506),
                                         labBut="Забанить", modal_def=ban_user, need_modal=False))
        self.add_item(PrivateVoiceButton(custom_id=custom_id, custom_id_add="closeOpen", row=3, emoji=guild.get_emoji(1232986508844072990),
                                         labBut="Закрыть/Открыть", modal_def=open_close, need_modal=False))
        self.add_item(PrivateVoiceButton(custom_id=custom_id, custom_id_add="invisVis", row=3, emoji=guild.get_emoji(1232986510299758614),
                                         labBut="Невидимый/Видимый", modal_def=visible_invis, need_modal=False))
        self.add_item(PrivateVoiceButton(custom_id=custom_id, custom_id_add="trust_user", row=4, emoji=guild.get_emoji(1232987824588849172),
                                         labBut="Доверить права", modal_def=trust_user, need_modal=False))

#----------------------------------------------------------------------
#Sqlite обновление данных

def sqliteUpdate(column: str, member_id:int, value):
    if isinstance(value, str):
        cursor.execute(f"UPDATE PrivateVoice SET {column} = '{value}' WHERE member_id = {member_id}")
        connection.commit()
    elif isinstance(value, int):
        cursor.execute(f"UPDATE PrivateVoice SET {column} = {value} WHERE member_id = {member_id}")
        connection.commit()

#----------------------------------------------------------------------
#Смена названия

async def channel_name(inter: discord.Interaction, newParameter:str):
    sqliteUpdate(column='name', member_id=inter.user.id, value = newParameter)
    await inter.channel.edit(name=newParameter)
    await inter.response.send_message(embed = userInteractionEmbed(
        interactionUser=inter, title="Изменение названия",
        descript=f"Вы поменяли название на **{newParameter}**"
        ), ephemeral=True)

#----------------------------------------------------------------------
#Лимит канала

async def channel_limit(inter: discord.Interaction, newParameter:str):
    if newParameter.isdigit():
        sqliteUpdate(column='voice_limit', member_id=inter.user.id, value = int(newParameter))
        await inter.channel.edit(user_limit=int(newParameter))
        await inter.response.send_message(embed = userInteractionEmbed(interactionUser=inter, title="Изменение лимита", descript=f"Вы поменяли лимит на **{newParameter}**"), ephemeral=True)
    else:
        await inter.response.send_message(embed = userInteractionEmbed(interactionUser=inter, title="Ошибка в изменении лимита", descript=f"Вы указали не число"), ephemeral=True)
        
#----------------------------------------------------------------------
#Взять владельца

async def take_owner(inter: discord.Interaction):
    user_chan = inter.user.voice.channel
    if inter.guild.get_member(cursor.execute(f"SELECT owner_id FROM PrivateVoiceOwner WHERE channel_id = {user_chan.id}").fetchone()[0]) in user_chan.members:
        await inter.response.send_message(embed = userInteractionEmbed(interactionUser=inter, title="Ошибка в получении прав", descript=f"Владелец не покинул свою приватку"), ephemeral=True)
    else:
        cursor.execute(f"UPDATE PrivateVoiceOwner SET owner_id = {inter.user.id} WHERE channel_id = {user_chan.id}")
        connection.commit()
        await inter.response.send_message(embed = userInteractionEmbed(interactionUser=inter, title="Обновление владельца", descript=f"Теперь вы владелец голосового канала"), ephemeral=True)

#----------------------------------------------------------------------
#Закрыть / открыть канал

async def open_close(inter: discord.Interaction):
    if in_private_voice(interact=inter):
        user_chan = inter.user.voice.channel
        have_permission = user_chan.permissions_for(inter.guild.default_role).connect
        new_perm = "закрытая"
        
        if have_permission:
            await user_chan.set_permissions(target=inter.guild.default_role, overwrite=discord.PermissionOverwrite(connect=False))
        else:
            await user_chan.set_permissions(target=inter.guild.default_role, overwrite=discord.PermissionOverwrite(connect=True))
            new_perm = "открытая"
            
        await inter.response.send_message(embed = userInteractionEmbed(interactionUser=inter, title="Обновление статуса приватки", descript=f"Теперь приватка имеет статус: **{new_perm}**"), 
                                          ephemeral=True) 
    
    else:
        await inter.response.send_message(embed = ready_embeds(iter=inter, embed_name="not_in_voice"), ephemeral=True)
        
#----------------------------------------------------------------------
#Спрятать / открыть канал

async def visible_invis(inter: discord.Interaction):
    if in_private_voice(interact=inter):
        user_chan = inter.user.voice.channel
        have_permission = user_chan.permissions_for(inter.guild.default_role).view_channel
        new_perm = "невидимая"
        
        if have_permission:
            await user_chan.set_permissions(target=inter.guild.default_role, overwrite=discord.PermissionOverwrite(view_channel = False))
        else:
            await user_chan.set_permissions(target=inter.guild.default_role, overwrite=discord.PermissionOverwrite(view_channel = True))
            new_perm = "видимая"
            
        await inter.response.send_message(embed = userInteractionEmbed(interactionUser=inter, title="Обновление статуса приватки", descript=f"Теперь приватка имеет статус: **{new_perm}***"), 
                                          ephemeral=True) 
    
    else:
        await inter.response.send_message(embed = ready_embeds(iter=inter, embed_name="not_in_voice"), ephemeral=True) 
        
#----------------------------------------------------------------------
#Передать права
class GIveOwnerSelectUser(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="Выберите пользователя", min_values=1, max_values=1)
        
    async def callback(self, interaction: discord.Interaction):
        new_owner = self.values[0]
        if in_private_voice(interact=interaction):
            new_own_chan = interaction.user.voice.channel
            cursor.execute(f"UPDATE PrivateVoiceOwner SET owner_id = {new_owner.id} WHERE channel_id = {new_own_chan.id}")
            connection.commit()
            await interaction.response.send_message(embed = userInteractionEmbed(interactionUser=interaction, title="Обновление владельца", 
                                                                                 descript=f"Теперь владелец голосового канала - {new_owner.mention}"), ephemeral=True)
        else:
            await interaction.response.send_message(embed = ready_embeds(iter=interaction, embed_name="not_in_voice"), ephemeral=True)

async def give_owner(inter: discord.Interaction):
    class giveOwner(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=180)
            
            self.add_item(GIveOwnerSelectUser())
    
    
    if in_private_voice(interact=inter):
        await inter.response.send_message(embed = userInteractionEmbed(interactionUser=inter, title="Обновление владельца", 
                                                                                 descript=f"Выберите нового владельца в меню ниже"), 
                                          view = giveOwner(), ephemeral = True)
        
    else:
        await inter.response.send_message(embed = ready_embeds(iter=inter, embed_name="not_in_voice"), ephemeral=True) 
        

#----------------------------------------------------------------------
#Забанить в голосовом канале

class banUserSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="Выберите пользователя(ей)", min_values=1, max_values=5)   
        
    async def callback(self, interaction: discord.Interaction):
        if in_private_voice(interact=interaction):
            #Приватка
            ban_channel = interaction.user.voice.channel
            #Выбранные пользователи
            users = self.values
            #Права
            overwrites={}
            #Тег пользователей
            usersMention = ""
            for i in range(len(users)):
                if i == 0: usersMention += f"<@{users[i].id}>"
                else: usersMention += f", <@{users[i].id}>"
                
                await ban_channel.set_permissions(target=users[i], overwrite=discord.PermissionOverwrite(connect=False, view_channel=True))
            
            #Кик юзеров
            for i in range(len(users)):
                if users[i] in ban_channel.members:
                    await users[i].move_to(None)
        
            await interaction.response.send_message(embed = userInteractionEmbed(interactionUser=interaction, title="Бан пользователей", 
                                                                                 descript=f"Были забанены в приватном голосовом канале: {usersMention}"), ephemeral=True)
        else:
            await interaction.response.send_message(embed = ready_embeds(iter=interaction, embed_name="not_in_voice"), ephemeral=True)
        
        
async def ban_user(inter: discord.Interaction):
    class Ban_UserView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=180)
            
            self.add_item(banUserSelect())
    
    if in_private_voice(interact=inter):
        await inter.response.send_message(embed = userInteractionEmbed(interactionUser=inter, title="Бан пользователей",
                                                                       descript=f"Выберите пользователей, которых хотите забанить."), 
                                          ephemeral=True, view=Ban_UserView())
                    
    else:
        await inter.response.send_message(embed = ready_embeds(iter=inter, embed_name="not_in_voice"), ephemeral=True)
        
#----------------------------------------------------------------------
#Сделать участника доверенным лицом

     
class TrustUserSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="Выберите пользователя(ей)", min_values=1, max_values=5)   
        
    async def callback(self, interaction: discord.Interaction):
        if in_private_voice(interact=interaction):
            #Приватка
            user_channel = interaction.user.voice.channel
            #Выбранные пользователи
            users = self.values
            #Права
            overwrites={}
            #Тег пользователей
            usersMention = ""
            for i in range(len(users)):
                if i == 0: usersMention += f"<@{users[i].id}>"
                else: usersMention += f", <@{users[i].id}>"
                
                await user_channel.set_permissions(target=users[i], overwrite=discord.PermissionOverwrite(view_channel=True, connect = True))
        
            await interaction.response.send_message(embed = userInteractionEmbed(interactionUser=interaction, title="Доверенные пользователи", 
                                                                                 descript=f"Добавлены новые доверенные участники: {usersMention}"), ephemeral=True)
        else:
            await interaction.response.send_message(embed = ready_embeds(iter=interaction, embed_name="not_in_voice"), ephemeral=True)
        
        
async def trust_user(inter: discord.Interaction):
    class Trust_UserView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=180)
            
            self.add_item(TrustUserSelect())
    
    if in_private_voice(interact=inter):
        await inter.response.send_message(embed = userInteractionEmbed(interactionUser=inter, title="Доверенные пользователи",
                                                                       descript=f"Выберите пользователей, которых хотите сделать доверенными."), 
                                          ephemeral=True, view=Trust_UserView())
                    
    else:
        await inter.response.send_message(embed = ready_embeds(iter=inter, embed_name="not_in_voice"), ephemeral=True)

#----------------------------------------------------------------------
#Настройки приватности


class SecurityMenu(discord.ui.Select):
    def __init__(self, *, custom_id: str, placeholder: str):
        options = [
            discord.SelectOption(label="Открыть", description="Открыть канал чтобы все могли заходить", value = "open"),
            discord.SelectOption(label="Закрыть", description="Закрыть канал чтобы никто не мог зайти", value = "close"),
            discord.SelectOption(label="Видимый", description="Сделать канал видимым для всех", value = "visible"),
            discord.SelectOption(label="Невидимый", description="Сделать канал невидимых для всех", value = "invisible")
        ]
        
        super().__init__(custom_id=custom_id, placeholder=placeholder, min_values=1, max_values=1, options=options)
        
    async def callback(self, interaction: discord.Interaction):
        answer = self.values[0]
        user_channel = interaction.user.voice.channel
        owner = interaction.guild.get_member(cursor.execute(f"SELECT owner_id FROM PrivateVoiceOwner WHERE channel_id = {user_channel.id}").fetchone()[0])
        
        if answer == 'visible':
            await user_channel.set_permissions(target=interaction.guild.default_role, overwrite=discord.PermissionOverwrite(view_channel=True))
            await user_channel.set_permissions(target=owner, overwrite=discord.PermissionOverwrite(view_channel=True))
            await interaction.response.send_message(embed=userInteractionEmbed(interactionUser=interaction, title="Изменение приватности",
                                                                               descript=f"Теперь канал имеет статус **видимый**."), ephemeral=True)
        elif answer == 'invisible':
            await user_channel.set_permissions(target=interaction.guild.default_role, overwrite=discord.PermissionOverwrite(view_channel=False))
            await user_channel.set_permissions(target=owner, overwrite=discord.PermissionOverwrite(view_channel=True))
            await interaction.response.send_message(embed=userInteractionEmbed(interactionUser=interaction, title="Изменение приватности",
                                                                               descript=f"Теперь канал имеет статус **невидимый**."), ephemeral=True)
        elif answer == 'open':
            await user_channel.set_permissions(target=interaction.guild.default_role, overwrite=discord.PermissionOverwrite(connect=True))
            await user_channel.set_permissions(target=owner, overwrite=discord.PermissionOverwrite(connect=True))
            await interaction.response.send_message(embed=userInteractionEmbed(interactionUser=interaction, title="Изменение приватности",
                                                                               descript=f"Теперь канал имеет статус **открытый**."), ephemeral=True)
        elif answer == 'close':
            await user_channel.set_permissions(target=interaction.guild.default_role, overwrite=discord.PermissionOverwrite(connect=False))
            await user_channel.set_permissions(target=owner, overwrite=discord.PermissionOverwrite(connect=True))
            await interaction.response.send_message(embed=userInteractionEmbed(interactionUser=interaction, title="Изменение приватности",
                                                                               descript=f"Теперь канал имеет статус **закрытый**."), ephemeral=True)

class SecurityMenuView(discord.ui.View):
    def __init__(self, inter: discord.Interaction):
            super().__init__(timeout=None)
            self.add_item(SecurityMenu(custom_id=f"{inter.user.voice.channel.id}", placeholder="Выберите опцию приватности"))

async def private_settings(inter: discord.Interaction):    
    await inter.response.send_message(embed=userInteractionEmbed(interactionUser=inter, title="Приватность",
                                                                 descript=f"Выберите настройки приватности, которые хотите изменить"
                                                                 ).set_footer(text="Выбирайте по одной настройке"),
                                      view=SecurityMenuView(inter),ephemeral=True)

#----------------------------------------------------------------------
#Основа приваток (создание, удаление)

class privatevoice(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    #Загрузка кнопок в приватках, после перезапуска
    @cmd.Cog.listener()
    async def on_ready(self):
        data = cursor.execute("SELECT * FROM PickRolesButtonsId").fetchall()
        for el in data:
            self.bot.add_view(PrivateVoiceView(custom_id=el[0],bot = self.bot))
            
        for guild in self.bot.guilds:
            for member in guild.members:
                if cursor.execute(f"SELECT member_id FROM PrivateVoice WHERE member_id = {member.id}").fetchone() is None:
                    cursor.execute(f'INSERT INTO PrivateVoice (member_id, name, voice_limit, bitrate) VALUES ({member.id}, "Приватка {member.name}", 0, 64)')
                    
        connection.commit()
    
    
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
                
                cursor.execute(f'INSERT INTO PrivateVoiceOwner(channel_id, owner_id, trust_users_id) VALUES ({private_voice.id}, {member.id}, "[]")')
                connection.commit()
                await private_voice.send(embed=discord.Embed(title="Управление приватной комнатой",
                                                             description="**Используйте кнопки ниже для управления своей приватной комнатой*", 
                                                             colour=discord.Color.from_str("#e310c0")
                                                             ), 
                                         view = PrivateVoiceView(private_voice.id, self.bot))
                
                
        
        if before.channel is not None:
            if before.channel in member.guild.get_channel(data[0]["PrivateVoice"]["privatevoice_category_id"]).channels and before.channel.id != data[0]["PrivateVoice"]["privatevoice_channel_id"]:
                if len(before.channel.members) == 0:
                    cursor.execute(f'DELETE FROM PrivateVoiceOwner WHERE channel_id = {before.channel.id}')
                    connection.commit()
                    await before.channel.delete()
        

                

async def setup(bot):
    await bot.add_cog(privatevoice(bot))