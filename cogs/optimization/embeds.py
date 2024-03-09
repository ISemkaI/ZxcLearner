import discord
from datetime import datetime as dt

def message_successfully_send():
    return discord.Embed(title="Сообщение успешно отправлено", color = discord.Color.from_str("#0dde2d"), timestamp=dt.utcnow())

def message_unsuccessfully_send():
    return discord.Embed(title="Сообщение не было отправлено", color = discord.Color.from_str("#e34a0e"), timestamp=dt.utcnow())

def message_command_error(error):
    return discord.Embed(title=f"При выполнении команды произошла ошибка: {error}", color = discord.Color.from_str("#ff0000"), timestamp=dt.utcnow())

 