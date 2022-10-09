import telebot
from telebot import types
import json
from time import time

sets = None
timeout = 0

with open("config.json",encoding="UTF-8") as file:
  config = json.loads(file.read())

with open("homework.json",encoding="UTF-8") as f:
  homework = json.loads(f.read())

bot=telebot.TeleBot(config["token"])

def log(Log):
  with open("messages.log","a",encoding="UTF-8") as f:
    f.write(Log+"\n")

def get_hw():
  global homework
  with open("homework.json",encoding="UTF-8") as f:
    homework =  json.loads(f.read())

def set_hw():
  global homework
  with open("homework.json","w",encoding="UTF-8") as f:
    f.write(json.dumps(homework,indent=4,ensure_ascii=False))

@bot.message_handler(commands=['start'])
def start_message(message):
  key = types.ReplyKeyboardMarkup(True)
  key.add(types.KeyboardButton("Что задали?"))
  bot.send_message(message.chat.id,f"Привет ✌️ {message.from_user.first_name}",reply_markup=key)
  print(f"{message.from_user.first_name}:{message.from_user.id}")

@bot.message_handler(commands=["homework"])
def get_homework(message):
  global homework

  get_hw()
  hw = ""
  for lesson in homework.items():
    hw += f"{lesson[0]} : {lesson[1]}\n"
  bot.send_message(message.chat.id,hw[:len(hw)-1])

@bot.message_handler(commands=["set"])
def set_homework(message):
  global homework
  global config
  global sets
  global timeout

  if not sets == None:
    if time()-timeout<=config["timeout"]:
      bot.send_message(message.chat.id,"Извини я занята")
      bot.send_message(sets[2],"Поторопись!")
      return
  sets=[0,0,message.chat.id]
  timeout = time()
  if message.chat.id in config["admins"]:
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for i in homework.keys():
      keyboard.add(types.InlineKeyboardButton(i,callback_data=f"sethw/{i}"))

    bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard)

@bot.message_handler(content_types=["text"])
def text(message):
  global sets
  global homework

  log(f"user_id:{message.from_user.id} | first_name:{message.from_user.first_name} | chat_id:{message.chat.id} | chat_title:{message.chat.title} | message_text:{message.text}")
  if message.text=="Что задали?": get_homework(message=message)

  if not sets==None:
    if message.chat.id == sets[2]:
      homework[sets[1]]=message.text
      bot.delete_message(message.chat.id,message.message_id)
      bot.edit_message_text(chat_id=message.chat.id,message_id=sets[0].message_id,text="👍")
      bot.send_message(message.chat.id,"Изменено!")
      sets = None
      set_hw()

@bot.callback_query_handler(lambda call: True)
def keyboard(call):
  global sets

  if call.message:
    data = call.data.split("/")
    if data[0] == "sethw":
      sets = [call.message,data[1],call.message.chat.id]
      bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=data[1])

bot.infinity_polling()