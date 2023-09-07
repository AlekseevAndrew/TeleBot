import os
import telebot
from telebot import types
import json
from time import time

setc = None
sets = None
setsh = None
sendf = None
stikers = {}
timeout = 0
users = {}
homework = {}
schedule = []
scheduleLessons = []

if not "users.json" in os.listdir():
  with open("users.json","w",encoding="UTF-8") as file:
    file.write("{}")

def init():
  global users, helpText, config, homework, schedule, scheduleLessons

  with open("users.json",encoding="UTF-8") as file:
    users = json.loads(file.read())

  with open("config.json",encoding="UTF-8") as file:
    config = json.loads(file.read())

  with open("homework.json",encoding="UTF-8") as f:
    homework = json.loads(f.read())

  with open(config["help"],encoding="UTF-8") as f:
    helpText = f.read()

  with open("schedule.json",encoding="UTF-8") as f:
    schedule = json.loads(f.read())
  
  with open("scheduleLessons.json",encoding="UTF-8") as f:
    scheduleLessons = json.loads(f.read())

init()

bot=telebot.TeleBot(config["token"])

convertId = lambda id: int(id) if id.isdigit() else str(id)

def log(Log):
  with open("messages.log","a",encoding="UTF-8") as f:
    f.write(Log+"\n")

def get_schl():
  global scheduleLessons
  with open("scheduleLessons.json",encoding="UTF-8") as f:
    scheduleLessons =  json.loads(f.read())

def set_schl():
  global scheduleLessons
  with open("scheduleLessons.json","w",encoding="UTF-8") as f:
    f.write(json.dumps(scheduleLessons,indent=4,ensure_ascii=False))

def get_sch():
  global schedule
  with open("schedule.json",encoding="UTF-8") as f:
    schedule =  json.loads(f.read())

def set_sch():
  global schedule
  with open("schedule.json","w",encoding="UTF-8") as f:
    f.write(json.dumps(schedule,indent=4,ensure_ascii=False))

def get_hw():
  global homework
  with open("homework.json",encoding="UTF-8") as f:
    homework =  json.loads(f.read())

def set_hw():
  global homework
  with open("homework.json","w",encoding="UTF-8") as f:
    f.write(json.dumps(homework,indent=4,ensure_ascii=False))

def user(message):
  global users
  if not str(message.from_user.id) in list(users.keys()):
    users[str(message.from_user.id)]={"username":message.from_user.username,"first_name":message.from_user.first_name,"last_name":message.from_user.last_name}
    with open("users.json","w",encoding="UTF-8") as file:
      file.write(json.dumps(users,indent=4,ensure_ascii=False))

def get_message_type(message):
  if not message.animation == None: return "animation"
  elif not message.audio == None: return "audio"
  elif not message.photo == None: return "photo"
  elif not message.voice == None: return "voice"
  elif not message.video == None: return "video"
  elif not message.video_note == None: return "video_note"
  elif not message.document == None: return "document"
  elif not message.sticker == None: return "sticker"
  elif not message.location == None: return "location"
  elif not message.contact == None: return "contact"

@bot.message_handler(commands=['start'])
def start_message(message):
  key = types.ReplyKeyboardMarkup(True)
  key.add(types.KeyboardButton("Что задали?"))
  key.add(types.KeyboardButton("Какое расписание?"))
  bot.send_message(message.chat.id,f"Привет ✌️ {message.from_user.first_name}",reply_markup=key,parse_mode="markdown")
  print(f"{message.from_user.first_name}:{message.from_user.id}")

@bot.message_handler(commands=["addLesson"])
def addLesson(message):
  if message.chat.id in config["moderators"]:
    name = message.text.split()[1:]
    homework[name] = "-"
    bot.delete_message(message.chat.id,message.message_id)
    bot.send_message(message.chat.id,"👍",parse_mode="markdown")
    bot.send_message(message.chat.id,"Добавлено!",parse_mode="markdown")
    set_hw()
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["deleteLesson"])
def deleteLesson(message):
  if message.chat.id in config["moderators"]:
    get_hw()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for i in homework.keys():
      keyboard.add(types.InlineKeyboardButton(i,callback_data=f"delhwl/{i}"))

    bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard,parse_mode="markdown")
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["addSLesson"])
def addLesson(message):
  if message.chat.id in config["moderators"]:
    name = message.text.split()[1:]
    scheduleLessons.append(name)
    bot.delete_message(message.chat.id,message.message_id)
    bot.send_message(message.chat.id,"👍",parse_mode="markdown")
    bot.send_message(message.chat.id,"Добавлено!",parse_mode="markdown")
    set_schl()
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["deleteSLesson"])
def deleteLesson(message):
  if message.chat.id in config["moderators"]:
    get_schl()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for i in scheduleLessons:
      keyboard.add(types.InlineKeyboardButton(i,callback_data=f"delshl/{i}"))

    bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard,parse_mode="markdown")
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["setSchedule"])
def setSchedule(message):
  global setsh
  if message.chat.id in config["moderators"]:
    setsh=[{},bot.send_message(message.chat.id,"С какого урока?").message_id,message.chat.id,0,0,0]
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["sendText"])
def text(message):
  txt = message.text.split()
  bot.send_message(convertId(txt[1])," ".join(txt[2:len(txt)]),parse_mode="markdown")

@bot.message_handler(commands=["log"])
def printLog(message):
  if message.chat.id in config["moderators"]:
    with open("messages.log") as f:
      if f.read()=="":
        bot.send_message(message.chat.id,"Логи пусты!",parse_mode="markdown")
        return
    bot.send_document(message.chat.id,types.InputFile("messages.log"))
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["clearLog"])
def clearLog(message):
  if message.chat.id==config["administrator"]:
    with open("messages.log","w") as file:file.write("")
    bot.send_message(message.chat.id,"Отчистила логи.",parse_mode="markdown")
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["version"])
def version(message):
  global config
  bot.send_message(message.chat.id,str(config["version"]),parse_mode="markdown")

@bot.message_handler(commands=["users"])
def usersLog(message):
  if message.chat.id==config["administrator"]:
    with open("users.json") as f:
      if f.read()=="":
        bot.send_message(message.chat.id,"пусто",parse_mode="markdown")
        return
    bot.send_document(message.chat.id,types.InputFile("users.json"))
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["shutdown"])
def shutdown(message):
  global config
  if message.chat.id==config["administrator"]:
    bot.send_message(message.chat.id,"выключаю компьютер",parse_mode="markdown")
    os.system("shutdown /p")
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["config"])
def shutdown(message):
  global config
  if message.chat.id==config["administrator"]:
    with open("config.json") as f:
      if f.read()=="":
        bot.send_message(message.chat.id,"пусто",parse_mode="markdown")
        return
    bot.send_document(message.chat.id,types.InputFile("config.json"))
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["raise"])
def shutdown(message):
  global config
  if message.chat.id==config["administrator"]:
    bot.stop_polling()
    exit()
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["setconfig"])
def setconfig(message):
  global config
  if message.chat.id==config["administrator"]:
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for i in config.keys():
      keyboard.add(types.InlineKeyboardButton(i,callback_data=f"setc/{i}"))
    bot.send_message(message.chat.id,"Настройка",reply_markup=keyboard,parse_mode="markdown")
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["help"])
def help(message):
  global helpText
  bot.send_message(message.chat.id,helpText,parse_mode="markdown")

@bot.message_handler(commands=["id"])
def get_my_id(message):
  bot.send_message(message.chat.id,message.chat.id,parse_mode="markdown")

@bot.message_handler(commands=["reload"])
def reload_sys(message):
  global config
  if message.chat.id==config["administrator"]:
    bot.send_message(message.chat.id,"Перезагрузка!")
    bot.stop_polling()
    os.system(config["startCommand"])
    exit()
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["sendFile"])
def sendFile(message):
  global sendf
  sendf = [message.chat.id,convertId(message.text.split()[1])]
  bot.send_message(message.chat.id,f"что отправить пользователю {message.text.split()[1]}?")

@bot.message_handler(content_types=['animation', 'audio', 'photo', 'voice', 'video', 'video_note', 'document', 'sticker', 'location', 'contact'])
def check_file(message):
  user(message)
  Type = get_message_type(message)  

  global sendf
  if (not sendf == None) and sendf[0] == message.chat.id:
    ID = sendf[1]
    if Type == "animation": bot.send_animation(ID, message.animation.file_id)
    elif Type == "audio": bot.send_audio(ID, message.audio.file_id)
    elif Type == "photo": bot.send_photo(ID, message.photo.file_id, caption=message.caption)
    elif Type == "voice": bot.send_voice(ID, message.voice.file_id)
    elif Type == "video": bot.send_video(ID, message.video.file_id, caption=message.caption)
    elif Type == "video_note": bot.send_video_note(ID, message.video_note.file_id)
    elif Type == "document": bot.send_document(ID, message.document.file_id, caption=message.caption)
    elif Type == "sticker": bot.send_sticker(ID, message.sticker.file_id)
    elif Type == "location": bot.send_location(ID, message.location.latitude, message.location.longitude)
    elif Type == "contact": bot.send_contact(ID, message.contact.phone_number, message.contact.first_name)
    bot.send_message(message.chat.id,f"отправлено пользователю {ID}")
    sendf = None
    return

@bot.message_handler(commands=["homework"])
def get_homework(message):
  global homework

  get_hw()
  hw = ""
  for lesson in homework.items():
    hw += f"{lesson[0]} : {lesson[1]}\n"
  bot.send_message(message.chat.id,hw[:len(hw)-1],parse_mode="markdown")

@bot.message_handler(commands=["set"])
def set_homework(message):
  global homework
  global config
  global sets
  global timeout

  if not sets == None:
    if time()-timeout<=config["timeout"]:
      bot.send_message(message.chat.id,"Извини я занята",parse_mode="markdown")
      bot.send_message(sets[2],"Поторопись!",parse_mode="markdown")
      return
  timeout = time()
  if message.chat.id in config["moderators"]:
    sets=[None,None,message.chat.id]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for i in homework.keys():
      keyboard.add(types.InlineKeyboardButton(i,callback_data=f"sethw/{i}"))

    bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard,parse_mode="markdown")
  else:bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!",parse_mode="markdown")

@bot.message_handler(commands=["schedule"])
def getSchedule(message):
  get_sch()
  c = schedule[0]
  less = schedule[1:]
  res = ""
  maxl = 0
  for i,lesson in enumerate(less):maxl = max(maxl,len(lesson["name"]))
  for i,lesson in enumerate(less):
    name = lesson["name"]
    cab = lesson["cab"]
    lname = ((maxl-len(name))*"--")
    res += f"_{i+c}_: *{name}*: {cab}\n"
  bot.send_message(message.chat.id,res[:len(res)-1],parse_mode="markdown")

@bot.message_handler(content_types=["text"])
def text(message):
  global sets, homework, setc, config, setsh, schedule

  user(message)
  log(f"{message.chat.id}/{message.from_user.id}:{message.text}")
  if message.text in config["getHomeworkCommands"]: get_homework(message=message)
  if message.text in config["getScheduleCommands"]: getSchedule(message=message)

  if not sets==None:
    if message.chat.id == sets[2] and (not sets[0] == None):
      homework[sets[1]]=message.text
      bot.delete_message(message.chat.id,message.message_id)
      bot.edit_message_text(chat_id=message.chat.id,message_id=sets[0].message_id,text="👍")
      bot.send_message(message.chat.id,"Изменено!",parse_mode="markdown")
      sets = None
      set_hw()

  if not setsh==None:
    if message.chat.id == setsh[2]:
      if setsh[3] == 0:
        st = int(message.text)
        setsh[5] = st
        setsh[3]=2
        bot.edit_message_text(message_id=setsh[1],text=f"Сколько уроков?",chat_id=setsh[2],parse_mode="markdown")
        bot.delete_message(message.chat.id,message.message_id)
      if setsh[3] == 1:
        cab = (message.text)
        schedule.append({"name":setsh[0],"cab":cab})
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        les = len(schedule)-1
        for i in scheduleLessons:
          keyboard.add(types.InlineKeyboardButton(i,callback_data=f"setshl/{i}/{les}"))
        bot.edit_message_text(message_id=setsh[1],text=f"Какой {les+1} урок?",chat_id=setsh[2],reply_markup=keyboard,parse_mode="markdown")
        bot.delete_message(message.chat.id,message.message_id)
        if les == setsh[4]:
          bot.edit_message_text(message_id=setsh[1],text=f"👍",chat_id=setsh[2],parse_mode="markdown")
          bot.send_message(message.chat.id,"Изменено!",parse_mode="markdown")
          setsh = None
          set_sch()
      if setsh[3] == 2:
        setsh[3]=1
        less = int(message.text)
        setsh[4] = less
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for i in scheduleLessons:
          keyboard.add(types.InlineKeyboardButton(i,callback_data=f"setshl/{i}/0"))
        bot.edit_message_text(message_id=setsh[1],text="Какой 1 урок?",chat_id=setsh[2],reply_markup=keyboard,parse_mode="markdown")
        bot.delete_message(message.chat.id,message.message_id)
        schedule = [setsh[5]]

  if message.chat.id == config["administrator"]:
    if not setc==None:
      config[setc]=eval(message.text)
      with open("config.json","w",encoding="UTF-8") as f:
        f.write(json.dumps(config,indent=4,ensure_ascii=False))

@bot.callback_query_handler(lambda call: True)
def keyboard(call):
  global sets,setc,setsh

  if call.message:
    data = call.data.split("/")
    if data[0] == "sethw":
      sets = [call.message,data[1],call.message.chat.id]
      bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=data[1])
    if data[0] == "setc":
      setc = data[1]
      bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=config[data[1]])
    if data[0] == "delhwl":
      del homework[data[1]]
      set_hw()
      bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="👍")
      bot.send_message(call.message.chat.id,"Готово!",parse_mode="markdown")
    if data[0] == "setshl":
      setsh[0]  = data[1]
      bot.edit_message_text(message_id=setsh[1],text="Какой кбинет?",chat_id=setsh[2],parse_mode="markdown")
    if data[0] == "delshl":
      scheduleLessons.remove(data[1])
      set_schl()
      bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="👍")
      bot.send_message(call.message.chat.id,"Готово!",parse_mode="markdown")

bot.infinity_polling()