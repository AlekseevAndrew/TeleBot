from time import time

bot = None
bot_config = None
config = None

def awake(bot_,bot_config_,config_):
    global bot,bot_config,config
    bot = bot_
    bot_config = bot_config_
    config = config_

def setup():
    @bot.message_handler(commands=['aboba'])
    def aboba(message):
        bot.send_message(message.chat.id,"ABOBA")

def tick():
    pass