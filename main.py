import os
import telebot
from telebot import types
import json
import pyttsx3
from time import time

setc = None
speaker = pyttsx3.init()
sets = None
stikers = {}
timeout = 0
users = {}

if not "users.json" in os.listdir():
  with open("users.json","w",encoding="UTF-8") as file:
    file.write("{}")

with open("users.json",encoding="UTF-8") as file:
  users = json.loads(file.read())

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

def user(message): #1.3
  global users
  if not str(message.from_user.id) in list(users.keys()):
    users[message.from_user.id]={"username":message.from_user.username,"first_name":message.from_user.first_name,"last_name":message.from_user.last_name}
    with open("users.json","w",encoding="UTF-8") as file:
      file.write(json.dumps(users,indent=4,ensure_ascii=False))

@bot.message_handler(commands=['start'])
def start_message(message):
  key = types.ReplyKeyboardMarkup(True)
  key.add(types.KeyboardButton("Что задали?"))
  bot.send_message(message.chat.id,f"Привет ✌️ {message.from_user.first_name}",reply_markup=key)
  print(f"{message.from_user.first_name}:{message.from_user.id}")

@bot.message_handler(commands=["sendText"]) #1.1
def text(message):
  txt = message.text.split()
  bot.send_message(int(txt[1])," ".join(txt[2:len(txt)]))

@bot.message_handler(commands=["sendVoice"]) #1.1
def text(message):
  global speaker
  txt = message.text.split()
  speaker.save_to_file(" ".join(txt[2:len(txt)]),"voice.mp3")
  speaker.runAndWait()
  bot.send_voice(int(txt[1]),types.InputFile("voice.mp3"))

@bot.message_handler(commands=["log"]) #1.2
def printLog(message):
  with open("messages.log") as f:
    if f.read()=="":
      bot.send_message(message.chat.id,"Логи пусты!")
      return
  bot.send_document(message.chat.id,types.InputFile("messages.log"))

@bot.message_handler(commands=["clearLog"]) #1.2
def clearLog(message):
  with open("messages.log","w") as file:file.write("")
  bot.send_message(message.chat.id,"Отчистила логи.")

@bot.message_handler(commands=["version"]) #1.3
def version(message):
  global config
  bot.send_message(message.chat.id,str(config["version"]))

@bot.message_handler(commands=["users"]) #1.3
def usersLog(message):
  with open("users.json") as f:
    if f.read()=="":
      bot.send_message(message.chat.id,"пусто")
      return
  bot.send_document(message.chat.id,types.InputFile("users.json"))

@bot.message_handler(commands=["shutdown"]) #1.4
def shutdown(message):
  global config
  if message.chat.id==config["administrator"]:
    bot.send_message(message.chat.id,"выключаю компьютер")
    os.system("shutdown /p")
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["config"]) #1.4
def shutdown(message):
  global config
  if message.chat.id==config["administrator"]:
    with open("config.json") as f:
      if f.read()=="":
        bot.send_message(message.chat.id,"пусто")
        return
    bot.send_document(message.chat.id,types.InputFile("config.json"))
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["raise"]) #1.4
def shutdown(message):
  global config
  if message.chat.id==config["administrator"]:
    bot.send_message(message.chat.id,"выключаю систему. пожалуйста наришите чтонибудь")
    bot.stop_polling()
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["setconfig"]) #1.4
def setconfig(message):
  global config
  if message.chat.id==config["administrator"]:
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for i in config.keys():
      keyboard.add(types.InlineKeyboardButton(i,callback_data=f"setc/{i}"))
    bot.send_message(message.chat.id,"Настройка",reply_markup=keyboard)
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

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
  timeout = time()
  if message.chat.id in config["admins"]:
    sets=[0,0,message.chat.id]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for i in homework.keys():
      keyboard.add(types.InlineKeyboardButton(i,callback_data=f"sethw/{i}"))

    bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard)

@bot.message_handler(content_types=["text"])
def text(message):
  global sets
  global setc
  global homework
  global config

  user(message)
  log(f"{message.from_user.id}:{message.text}")
  if message.text=="Что задали?": get_homework(message=message)

  if not sets==None:
    if message.chat.id == sets[2]:
      homework[sets[1]]=message.text
      bot.delete_message(message.chat.id,message.message_id)
      bot.edit_message_text(chat_id=message.chat.id,message_id=sets[0].message_id,text="👍")
      bot.send_message(message.chat.id,"Изменено!")
      sets = None
      set_hw()

  if message.chat.id == config["administrator"]:
    if not setc==None:
      config[setc]=eval(message.text)
      with open("config.json","w") as f:
        f.write(json.dumps(config,indent=4,ensure_ascii=False))

@bot.callback_query_handler(lambda call: True)
def keyboard(call):
  global sets
  global setc

  if call.message:
    data = call.data.split("/")
    if data[0] == "sethw":
      sets = [call.message,data[1],call.message.chat.id]
      bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=data[1])
    if data[0] == "setc":
      setc = data[1]
      bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=config[data[1]])

bot.infinity_polling()