#Discord
from typing import List
import discord
from discord import ButtonStyle
from discord.ext import commands as cmd
from discord.ui import View, Button
#Хранение
import datetime as dt

#--------------------------------------------------------------

filename_blacklist = [
    'application', 'exe', 'appimage', 'msi', 'msp',
    'sys', 'bat', 'cmd', 'dll', 
    'com', 'pif', 'cpl', 'gadget', 'hta', 'msc', 'scr']
filename_half_blacklist = [
    'zip', 'rar', '7z',
    'txt',
    'jar', 'js', 'jse',
    'vb', 'vbs', 'vbe', 'scf', 'inf', 'lnk', 
    'ws', 'wsf', 'wsc', 'wsh',
    'ps1', 'ps1xml', 'ps2', 'ps2xml', 'psc1', 'psc2']

moders = [1158028188564336754, 978947012546400288, 985368512887402537]
ignoring_category = [956118594855501845, 1149760908684431471, 1210155945418555422]
ignoring_roles = [1158028188564336754, 978947012546400288, 985368512887402537]
aswer_channel = 1210155843639574569

#--------------------------------------------------------------

async def LinkBan(interaction:discord.Interaction, member_id: int):
    moderator = interaction.user
    member = interaction.guild.get_member(member_id)
    await interaction.response.defer()
    await member.send(embed=discord.Embed(title="Бан",
                                          description=f"Вы были забанены на сервере {interaction.guild.name}.\nЕсли вы не согласны с решением, напишите <@1064888272393875527>",
                                          color=discord.Color.red()).set_image(url="https://media.discordapp.net/attachments/1204388122176258078/1230438409567207424/3f1bc03276d284a4.jpg").set_footer(text="Пишите особенно если вас взломали. Всех любим."))
    await member.edit(timed_out_until=None)
    await member.ban(delete_message_days=1, reason="Распространие ссылок на другие дискорд сервера")
    await interaction.followup.send(embed=discord.Embed(title="Участник был забанен", 
                                                        description=f"Был забанен: {member.mention}\n Подтвердил модератор: {moderator.mention}").set_author(name=moderator.name,
                                                                                                                                       icon_url=moderator.avatar))
    try: await interaction.message.delete()
    except Exception: pass
    
async def SaveTimeout(interaction:discord.Interaction, member_id: int):
    moderator = interaction.user
    member = interaction.guild.get_member(member_id)
    await interaction.response.defer()
    await interaction.followup.send(embed=discord.Embed(title="Сохранение наказания", 
                                                        description=f"Наказание было оставлено у: {member.mention}\n Подтвердил модератор: {moderator.mention}").set_author(name=moderator.name,
                                                                                                                                       icon_url=moderator.avatar))
    
    try: await interaction.message.delete()
    except Exception: pass
    
async def RemoveTimeout(interaction:discord.Interaction, member_id: int):
    moderator = interaction.user
    member = interaction.guild.get_member(member_id)
    await interaction.response.defer()
    await member.edit(timed_out_until=None)
    await interaction.followup.send(embed=discord.Embed(title="Снятие наказания", 
                                                        description=f"Наказание было снято у: {member.mention}\n Подтвердил модератор: {moderator.mention}").set_author(name=moderator.name,
                                                                                                                                       icon_url=moderator.avatar))
    
    try: await interaction.message.delete()
    except Exception: pass


async def NOOOO(interaction:discord.Interaction, member_id: int, mess_to_del: discord.Message):
    await interaction.response.send_message(embed = discord.Embed(title="Окей, не ошибайтесь больше"), ephemeral=True)
    try: await interaction.message.delete()
    except Exception: pass
    embs = mess_to_del.embeds[0]
    await mess_to_del.edit(embed=embs, view=linkView(member_id, False))

class FuncView(View):
    def __init__(self, member_id: int, interaction_moder: int, func):
        super().__init__(timeout=120)
        self.add_item(funcButton(custom_id=f"Yes:{member_id}", 
                                 member_id=member_id, 
                                 label_but="Да", style = ButtonStyle.green,
                                 func = func, auth_mod=interaction_moder))
        self.add_item(funcButton(custom_id=f"No:{member_id}", 
                                 member_id=member_id,
                                 label_but="Нет", style = ButtonStyle.red,
                                 func = NOOOO, auth_mod=interaction_moder))

class funcButton(Button):
    def __init__(self, custom_id: str, member_id:int, label_but: str, style:ButtonStyle, auth_mod: int, func):
        super().__init__(style=style, label=label_but, custom_id=custom_id)
        self.member_id = member_id
        self.func = func
        self.auth_mod = auth_mod
    
    async def callback(self, interaction: discord.Interaction):
        if self.auth_mod == interaction.user.id:
            await self.func(interaction, self.member_id)
        else:
            await interaction.response.send_message(content="Вы не можете использовать эту кнопку", ephemeral=True)

#----------------------------------------------------------------------------

class ReallyButton(Button):
    def __init__(self, custom_id: str, member_id:int, label_but: str, style:ButtonStyle, disable:bool,func):
        super().__init__(style=style, label=label_but, custom_id=custom_id, disabled=disable)
        self.member_id = member_id
        self.func = func
    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        flag = False
        for role_id in moders:
            if guild.get_role(role_id) in user.roles:
                flag = True
                break
        
        if flag:
            emb = interaction.message.embeds[0]
            await interaction.message.edit(embed=emb, view=linkView(self.member_id, True))
            await interaction.response.send_message(embed=discord.Embed(title='Вы уверены?'), view=FuncView(self.member_id, interaction.user.id, self.func))
        else:
            await interaction.response.send_message(embed=discord.Embed(title='У вас недостаточно прав'), ephemeral=True)
        
class linkView(View):
    def __init__(self, member_id: int, disable:bool):
        super().__init__(timeout=None)
        self.add_item(ReallyButton(custom_id=f"{member_id}:Ban", member_id=member_id, label_but="Забанить", style=ButtonStyle.grey, disable=disable,func=LinkBan))
        self.add_item(ReallyButton(custom_id=f"{member_id}:TimeOut", member_id=member_id, label_but="Таймаут остаётся", style=ButtonStyle.grey, disable=disable, func=SaveTimeout))
        self.add_item(ReallyButton(custom_id=f"{member_id}:UnTimeOut", member_id=member_id, label_but="Размутить", style=ButtonStyle.grey, disable=disable, func=RemoveTimeout))

#--------------------------------------------------------------

async def LinkInMessage(self, message:discord.Message):
    if 'discord.gg' in message.content or 'discord.com/invite' in message.content:
        ignoring_channels = [self.bot.get_channel(c) for c in ignoring_category]
        if message.channel.category not in ignoring_channels:
            ignoring_roles = [message.guild.get_role(x) for x in ignoring_roles]
            author_roles = message.author.roles
            if all([role not in author_roles for role in ignoring_roles]):
                channel = message.guild.get_channel(aswer_channel)
                content = message.content
                ind = content.find('discord.gg/')+11
                if ind == 11:
                    content.find("discord.com/invite/")+19
                try:
                    invite:discord.Invite = await self.bot.fetch_invite('https://discord.gg/'+content[ind:ind+40].split(' ')[0])
                except Exception:
                    await message.delete()
                    return
                    
                if invite.guild.id != message.guild.id:
                    try:
                        await message.author.timeout(dt.timedelta(days=4), reason="Распространение ссылок на другие сервера. Если произошла ошибка напишите администрации.")
                        
                        await channel.send(embed=discord.Embed(title="Нарушение правила: 6.1 (Ссылки)", 
                                                    description=f"Сообщение содержало такую информацию: ```{message.content}```",
                                                    color=discord.Color.red()).add_field(name="Автор", 
                                                                                        value=f"{message.author.mention}").add_field(name="Канал", 
                                                                                                                                    value=f"<#{message.channel.id}>"), 
                                    view = linkView(member_id=message.author.id, disable=False))
                    except Exception:
                        await channel.send(embed=discord.Embed(title="Нарушение правила: 6.1 (Ссылки)", 
                                                    description=f"Сообщение содержало такую информацию: ```{message.content}```",
                                                    color=discord.Color.red()).add_field(name="Автор", 
                                                                                        value=f"{message.author.mention}").add_field(name="Канал", 
                                                                                                                                    value=f"<#{message.channel.id}>").set_footer(text="У бота недостаточно прав."), 
                                    view = linkView(member_id=message.author.id, disable=True))
                    
                    await message.delete()
                    return


class automod(cmd.Cog):
    #Получение бота в нашу среду self
    def __init__(self, bot):
        self.bot = bot
        """except Exception:
            cursor.execute(f'DELETE FROM PickRolesButtonsId WHERE channel_id = {el[0]}')
            connection.commit()"""
    
    @cmd.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: return
        
        if len(message.attachments) > 0:
            for el in message.attachments:
                extension = el.filename.split('.')[-1]
                if extension in filename_blacklist:
                    await message.author.timeout(dt.timedelta(minutes=10), reason="Распространение запрещённых файлов, в которых могут находиться вирусы.\nВ случае ошибки свяжитесь с администрацией")
                    await message.delete()
                    return
                elif extension in filename_half_blacklist:
                    await message.channel.send(embed=discord.Embed(title="Опасность", color=discord.Color.yellow(), 
                                                                   description=f"Участник {message.author.mention} отправил сообщение с файлом(ами), в которых могут находиться вирусы.").set_footer(
                                                                       text="Бот может ошибаться. Содержимое файлов он не читает."
                                                                   ))
        
            await LinkInMessage(self=self, message=message)

    @cmd.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot: return
        await LinkInMessage(self=self, message=after)
        
async def setup(bot):
    await bot.add_cog(automod(bot))