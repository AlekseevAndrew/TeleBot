import os
import telebot
import json
import shutil
import datetime
import asyncio
import uuid
import random
import aiofiles
import aiohttp
from time import time
from telebot import async_telebot
from io import BytesIO

sets = None
setsh = None
sendf = None
stikers = {}
timeout = 0
users = {}
homework = {}
schedule = []
scheduleLessons = []
photos = []
blacklist = []
lastMessages = {}
chat_messages_before_homework_get = 10000
is_homework_updated = True
chat_messages_before_schedule_get = 10000
is_schedule_updated = True
reminds = []
reminders = {}
event_creators = {}

if not "users.json" in os.listdir():
  with open("users.json","w",encoding="UTF-8") as file:
    file.write("{}")

if not "blacklist.json" in os.listdir():
  with open("blacklist.json","w",encoding="UTF-8") as file:
    file.write("[]")

if not "reminds.json" in os.listdir():
  with open("reminds.json","w",encoding="UTF-8") as file:
    file.write("[]")

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

def get_blacklist():
  global blacklist
  with open("blacklist.json",encoding="UTF-8") as f:
    blacklist = json.loads(f.read())

def set_blacklist():
  global blacklist
  with open("blacklist.json","w",encoding="UTF-8") as f:
    f.write(json.dumps(blacklist,indent=4,ensure_ascii=False))

def get_reminds():
  global reminds
  with open("reminds.json",encoding="UTF-8") as f:
    reminds = json.loads(f.read())

def set_reminds():
  global reminds
  with open("reminds.json","w",encoding="UTF-8") as f:
    f.write(json.dumps(reminds,indent=4,ensure_ascii=False))

def init():
  global users, helpText, config

  with open("users.json",encoding="UTF-8") as file:
    users = json.loads(file.read())

  with open("config.json",encoding="UTF-8") as file:
    config = json.loads(file.read())

  with open(config["help"],encoding="UTF-8") as f:
    helpText = f.read()

  get_hw()
  get_sch()
  get_schl()
  get_blacklist()
  get_reminds()

init()

if config["netSchool"]["enable"]:from netschoolapi import NetSchoolAPI
if config["dnevnik_egov66"]["enable"]:
  import dnevnikEgov66Api
  dnevnikEgov66 = dnevnikEgov66Api.diary(config["dnevnik_egov66"]["login"],config["dnevnik_egov66"]["password"])

bot=async_telebot.AsyncTeleBot(config["token"],parse_mode="markdown")

convertId = lambda id: int(id) if id.isdigit() else str(id)

def log(Log):
  with open("messages.log","a",encoding="UTF-8") as f:
    f.write(Log+"\n")

def user(message):
  global users
  get_blacklist()
  if not str(message.from_user.id) in list(users.keys()):
    users[str(message.from_user.id)]={"username":message.from_user.username,"first_name":message.from_user.first_name,"last_name":message.from_user.last_name,"warnings":0,"rang": 0,"score": 0,"secrets":[False,False]}
    with open("users.json","w",encoding="UTF-8") as file:
      file.write(json.dumps(users,indent=4,ensure_ascii=False))
  if message.text!=None:
    log(f"{message.chat.id}/{message.from_user.id}:{message.text}")
  return message.from_user.id in blacklist

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
  else: return "text"

@bot.message_handler(commands=['start'])
async def start_message(message):
  if user(message):return
  key = telebot.types.ReplyKeyboardMarkup(True,row_width=4)
  key.add(telebot.types.KeyboardButton(config["user_commands"]["getHomeworkCommands"][0]),
          telebot.types.KeyboardButton(config["user_commands"]["getScheduleCommands"][0]),
          telebot.types.KeyboardButton(config["user_commands"]["getPhotosCommands"][0]),
          telebot.types.KeyboardButton(config["user_commands"]["getFilesCommands"][0]),
          telebot.types.KeyboardButton(config["user_commands"]["GetEventsCommands"][0]))

  if config["netSchool"]["enable"]:key.add(telebot.types.KeyboardButton(config["netSchool"]['getNetSchoolHomeworkCommands'][0]))
  if config["dnevnik_egov66"]["enable"]:key.add(telebot.types.KeyboardButton(config["dnevnik_egov66"]['getHomeworkCommands'][0]))

  if message.chat.id in config["moderators"]:key.add(config["moderatorCommands"]["SetScheduleCommands"][0],
                                                     config["moderatorCommands"]["SetHomeworkCommands"][0],
                                                     telebot.types.KeyboardButton(config["moderatorCommands"]["CreateEventCommands"][0]),
                                                     telebot.types.KeyboardButton(config["moderatorCommands"]["DeleteEventCommands"][0]))

  if message.chat.id == config["administrator"]:key.add(config["administratorCommands"]["getLogCommands"][0],
                                                        config["administratorCommands"]["getUsersCommands"][0],
                                                        config["administratorCommands"]["getConfigCommands"][0],
                                                        config["administratorCommands"]["getBlackListCommands"][0])
    
  if message.chat.id == config["chat"] and message.from_user.id in config["moderators"]:key.add(config["moderatorCommands"]["PinMessageCommands"][0],
                                                                                                config["moderatorCommands"]["UnpinMessageCommands"][0],
                                                                                                config["moderatorCommands"]["UnpinMessagesCommands"][0])
    
  if message.chat.id != config["chat"]:
    key.add(telebot.types.KeyboardButton(config["user_commands"]["CreateRemindCommands"][0]),
            telebot.types.KeyboardButton(config["user_commands"]["ListRemindsCommands"][0]),
            telebot.types.KeyboardButton(config["user_commands"]["DeleteRemindCommands"][0]))
    
    if message.chat.id in config["moderators"]:
      key.add(telebot.types.KeyboardButton(config["moderatorCommands"]["CreateClassRemindCommands"][0]),
              telebot.types.KeyboardButton(config["moderatorCommands"]["ListClassRemindsCommands"][0]),
              telebot.types.KeyboardButton(config["moderatorCommands"]["DeleteClassRemindCommands"][0]))
    
  await bot.send_message(message.chat.id,f"Привет ✌️ {message.from_user.first_name}",reply_markup=key)

@bot.message_handler(commands=["addLesson"])
async def addLesson(message):
  if user(message):return
  if message.chat.id in config["moderators"]:
    name = " ".join(message.text.split()[1:])
    homework[name] = "-"
    await bot.delete_message(message.chat.id,message.message_id)
    await bot.send_message(message.chat.id,"👍")
    await bot.send_message(message.chat.id,"Добавлено!")
    set_hw()
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["deleteLesson"])
async def deleteLesson(message):
  if user(message):return
  if message.chat.id in config["moderators"]:
    get_hw()
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    for i in homework.keys():
      keyboard.add(telebot.types.InlineKeyboardButton(i,callback_data=f"delhwl/{i}"))

    await bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard)
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["addSLesson"])
async def addLesson(message):
  if user(message):return
  if message.chat.id in config["moderators"]:
    name = " ".join(message.text.split()[1:])
    scheduleLessons.append(name)
    await bot.delete_message(message.chat.id,message.message_id)
    await bot.send_message(message.chat.id,"👍")
    await bot.send_message(message.chat.id,"Добавлено!")
    set_schl()
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["deleteSLesson"])
async def deleteLesson(message):
  if user(message):return
  if message.chat.id in config["moderators"]:
    get_schl()
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    for i in scheduleLessons:
      keyboard.add(telebot.types.InlineKeyboardButton(i,callback_data=f"delshl/{i}"))

    await bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard)
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["setSchedule"])
async def setSchedule(message):
  if user(message):return
  global setsh
  if message.chat.id in config["moderators"]:
    m = await bot.send_message(message.chat.id,"С какого урока?")
    setsh=[{},m.message_id,message.chat.id,0,0,0]
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["sendText"])
async def text(message):
  if user(message):return
  txt = message.text.split()
  await bot.send_message(convertId(txt[1])," ".join(txt[2:len(txt)]))

@bot.message_handler(commands=["log"])
async def printLog(message):
  if user(message):return
  if message.chat.id in config["moderators"]:
    with open("messages.log") as f:
      if f.read()=="":
        await bot.send_message(message.chat.id,"Логи пусты!")
        return
    await bot.send_document(message.chat.id,telebot.types.InputFile("messages.log"))
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["clearLog"])
async def clearLog(message):
  if user(message):return
  if message.chat.id==config["administrator"]:
    with open("messages.log","w") as file:file.write("")
    await bot.send_message(message.chat.id,"Отчистила логи.")
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["version"])
async def version(message):
  if user(message):return
  await bot.send_message(message.chat.id,"4.0.2")

@bot.message_handler(commands=["users"])
async def usersLog(message):
  if user(message):return
  if message.chat.id==config["administrator"]:
    with open("users.json") as f:
      if f.read()=="":
        await bot.send_message(message.chat.id,"пусто")
        return
    await bot.send_document(message.chat.id,telebot.types.InputFile("users.json"))
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["config"])
async def get_config(message):
  if user(message):return
  global config
  if message.chat.id==config["administrator"]:
    await bot.send_document(message.chat.id,telebot.types.InputFile("config.json"))
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["raise"])
async def shutdown(message):
  if user(message):return
  global config
  if message.chat.id==config["administrator"]:
    exit()
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["help"])
async def help(message):
  if user(message):return
  global helpText
  await bot.send_message(message.chat.id,helpText)

@bot.message_handler(commands=["id"])
async def get_my_id(message):
  if user(message):return
  if message.reply_to_message == None: await bot.send_message(message.chat.id,message.chat.id)
  else: await bot.send_message(message.from_user.id,message.reply_to_message.from_user.id)

@bot.message_handler(commands=["reload"])
async def reload_sys(message):
  if user(message):return
  global config
  if message.chat.id==config["administrator"]:
    await bot.send_message(message.chat.id,"Перезагрузка!")
    bot.stop_polling()
    os.system(config["startCommand"])
    exit()
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["reinit"])
async def reload_sys(message):
  if user(message):return
  global config
  if message.chat.id==config["administrator"]:
    await bot.send_message(message.chat.id,"Инициализация!")
    init()
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["sendFile"])
async def sendFile(message):
  if user(message):return
  global sendf
  sendf = [message.chat.id,convertId(message.text.split()[1])]
  await bot.send_message(message.chat.id,f"что отправить пользователю {message.text.split()[1]}?")

@bot.message_handler(commands=["pin"])
async def pin_message(message):
  if user(message):return
  if message.chat.id == config["chat"] and message.from_user.id in config["moderators"]:
    if message.reply_to_message==None:
      await bot.pin_chat_message(message.chat.id,lastMessages[message.from_user.id])
    else:
      await bot.pin_chat_message(message.chat.id,message.reply_to_message.id)
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["unpin"])
async def unpin_message(message):
  if user(message):return
  if message.chat.id == config["chat"] and message.from_user.id in config["moderators"] and message.reply_to_message != None:
    await bot.unpin_chat_message(message.chat.id,message.reply_to_message.id)
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["unpinall"])
async def unpin_all_messages(message):
  if user(message):return
  if message.chat.id == config["chat"] and message.from_user.id in config["moderators"]:
    await bot.unpin_all_chat_messages(message.chat.id)
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["create_remind"])
async def create_remind(message):
  if user(message):return
  if message.chat.id == config["chat"]:return

  reminders[str(message.chat.id)] = [message.chat.id]
  await bot.send_message(message.chat.id,"Напишите на какой день поставить напоминание в формате dd.mm (например 01.12), а затем через пробел за сколько дней надо напомнить об этом (не обязательно). Например если вы напишите `01.12 1 3 5` то я напомню вам первого декабря и за 1, 3, 5 дней")

@bot.message_handler(commands=["list_reminds"])
async def list_reminds(message):
  if user(message):return
  get_reminds()
  result = "Ваши напоминания:\n"
  for remind in reminds:
    if remind["user"] == message.chat.id:
      result+="*"+remind["date"]+"* " + remind["text"] + "\n"
  await bot.send_message(message.chat.id,result)

@bot.message_handler(commands=["delete_remind"])
async def delete_remind(message):
  if user(message):return
  key = telebot.types.InlineKeyboardMarkup()
  key.add(telebot.types.InlineKeyboardButton("Все",callback_data="delete_remind/all"))
  get_reminds()
  for i,remind in enumerate(reminds):
    if remind["user"] == message.chat.id:
      key.add(telebot.types.InlineKeyboardButton("*"+remind["date"]+"* " + remind["text"] + "\n",callback_data=f"delete_remind/{i}"))
  key.add(telebot.types.InlineKeyboardButton("-Отмена-",callback_data="delete_remind/cancel"))
  await bot.send_message(message.chat.id,"Что удалить?",reply_markup=key)

@bot.message_handler(commands=["create_remind_for_all"])
async def create_remind_for_all(message):
  if user(message):return
  if message.chat.id == config["chat"]:return

  reminders[str(message.chat.id)] = [config["chat"]]
  await bot.send_message(message.chat.id,"В какой день напомнить?")

@bot.message_handler(commands=["list_reminds_for_all"])
async def list_reminds_for_all(message):
  if user(message):return
  get_reminds()
  result = " Напоминания класса:\n"
  for remind in reminds:
    if remind["user"] == config["chat"]:
      result+="*"+remind["date"]+"* " + remind["text"] + "\n"
  await bot.send_message(message.chat.id,result)

@bot.message_handler(commands=["delete_remind_for_all"])
async def delete_remind_for_all(message):
  if user(message):return
  key = telebot.types.InlineKeyboardMarkup()
  key.add(telebot.types.InlineKeyboardButton("Все",callback_data="delete_remind_for_all/all"))
  get_reminds()
  for i,remind in enumerate(reminds):
    if remind["user"] == config["chat"]:
      key.add(telebot.types.InlineKeyboardButton("*"+remind["date"]+"* " + remind["text"] + "\n",callback_data=f"delete_remind_for_all/{i}"))
  key.add(telebot.types.InlineKeyboardButton("-Отмена-",callback_data="delete_remind_for_all/cancel"))
  await bot.send_message(message.chat.id,"Что удалить?",reply_markup=key)

@bot.message_handler(commands=["get_events"])
async def get_events(message):
  if user(message):return
  key = telebot.types.InlineKeyboardMarkup()
  for dir in os.listdir("events/"):
    with open(f"events/{dir}/event_data.json",encoding="UTF_8") as f:
      event_data = json.loads(f.read())
    key.add(telebot.types.InlineKeyboardButton(event_data["name"],callback_data=f"get_event/{dir}"))
  key.add(telebot.types.InlineKeyboardButton("- Закрыть -",callback_data=f"get_event/close"))
  await bot.delete_message(message.chat.id,message.id)
  await bot.send_message(message.chat.id,"Доска объявлений:",reply_markup=key)

@bot.message_handler(["create_event"])
async def create_event(message):
  global event_creators
  if not message.chat.id in config["moderators"]:
    await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")
    return
  dir = str(uuid.uuid4().hex)
  os.mkdir(f"events/{dir}")
  event_creators[str(message.chat.id)] = [dir]
  await bot.send_message(message.chat.id,"Напишите название события")

@bot.message_handler(commands=["delete_event"])
async def delete_event(message):
  if user(message):return
  if not message.chat.id in config["moderators"]:
    await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")
    return
  key = telebot.types.InlineKeyboardMarkup()
  key.add(telebot.types.InlineKeyboardButton("- Все -",callback_data=f"delete_event/all"))
  for dir in os.listdir("events/"):
    with open(f"events/{dir}/event_data.json",encoding="UTF_8") as f:
      event_data = json.loads(f.read())
    key.add(telebot.types.InlineKeyboardButton(event_data["name"],callback_data=f"delete_event/{dir}"))
  key.add(telebot.types.InlineKeyboardButton("- Закрыть -",callback_data=f"delete_event/close"))
  await bot.send_message(message.chat.id,"Что удалить?",reply_markup=key)

@bot.message_handler(commands=["dnevnikEgov66"])
async def getDnevnikEgov66(message):
  if user(message):return
  if not config["dnevnik_egov66"]["enable"]:
    await bot.send_message(message.chat.id,"ОШИБКА: Данная функция отключена администраторм")
    return
  await bot.delete_message(message.chat.id,message.message_id)
  key = telebot.types.InlineKeyboardMarkup(row_width=4)
  key.add(telebot.types.InlineKeyboardButton("<3",callback_data="dnevnikEgov66/-1"),
          telebot.types.InlineKeyboardButton("<",callback_data="dnevnikEgov66/0"),
          telebot.types.InlineKeyboardButton(">",callback_data="dnevnikEgov66/2"),
          telebot.types.InlineKeyboardButton("3>",callback_data="dnevnikEgov66/4"),
          telebot.types.InlineKeyboardButton("<7",callback_data="dnevnikEgov66/-5"),
          telebot.types.InlineKeyboardButton("<5",callback_data="dnevnikEgov66/-3"),
          telebot.types.InlineKeyboardButton("5>",callback_data="dnevnikEgov66/6"),
          telebot.types.InlineKeyboardButton("7>",callback_data="dnevnikEgov66/8"))
  hw_raw = await dnevnikEgov66.getDayHomework(1)
  date = hw_raw["date"]
  hw = f"*{date}*\n\n"
  for i,lesson in enumerate(hw_raw["homework"]):
    name = lesson["name"]
    text = lesson["text"]
    hw += f"*{name}*\n`{text}`\n\n"
    if lesson["files"] != []:key.add(telebot.types.InlineKeyboardButton(f"*[{i}] {name}*",callback_data=f"dnevnikEgov66download/{date}/{i}"))
  if message.chat.id in config["moderators"]:key.add(telebot.types.InlineKeyboardButton("- Записать -",callback_data=f"dnevnikEgov66toBase/0/{date}"))
  key.add(telebot.types.InlineKeyboardButton("- Закрыть -",callback_data="dnevnikEgov66/close"))

  await bot.send_message(message.chat.id,hw,reply_markup=key)

@bot.message_handler(commands=["classinfo"])
async def getClassInfo(message):
  if user(message):return
  with open("classinfo.txt",encoding="UTF-8") as f:
    await bot.send_message(message.chat.id,f.read())

@bot.message_handler(commands=["birthdays"])
async def getBirthdays(message):
  if user(message):return
  with open("birthdays.json",encoding="UTF-8") as f:
    birthdays = json.loads(f.read())
  res = "Список дней рождения:\n"
  for birthday in birthdays:
    name = birthday["name"]
    date = birthday["date"]
    res += f"У *{name}* `{date}`\n"
  await bot.send_message(message.chat.id,res)

@bot.message_handler(commands=["rab"])
async def ball(message):
  if user(message):return
  if len(message.text)<7:
    await bot.reply_to(message,"Пожалуйста напишите что спросить у шара")
    return
  answer = random.choice(["Несомненно","Вероятно","Однозначно да","Нет","Да","Врядли","Точно нет","Очень может быть","Думаю да","Думаю что нет","Не могу сказать"])
  await bot.reply_to(message,answer)

@bot.message_handler(commands=["warn"])
async def sendWarning(message):
  if user(message):return
  if not message.from_user.id in config["moderators"]:
    await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")
    return
  if len(message.text)<7:
    await bot.reply_to(message,"Пожалуйста напишите о чем предупредить")
    return
  if message.reply_to_message == None:
    await bot.reply_to(message,"Пожалуйста напишите кого предупредить")
    return
  users[str(message.reply_to_message.from_user.id)]["warnings"]+=1
  with open("users.json","w",encoding="UTF-8") as file:
    file.write(json.dumps(users,indent=4,ensure_ascii=False))
  text = message.text[6:]
  number = users[str(message.reply_to_message.from_user.id)]["warnings"]
  await bot.send_message(message.reply_to_message.from_user.id,f"Вам выдано предупреждение {text}! (Случай #{number})")
  await bot.reply_to(message.reply_to_message,f"Выдано предупреждение {text}! (Случай #{number})")

@bot.message_handler(commands=["delwarn"])
async def clearWarnings(message):
  if user(message):return
  if not message.from_user.id in config["moderators"]:
    await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")
    return
  await bot.delete_message(message.chat.id,message.message_id)
  if message.reply_to_message == None:
    await bot.reply_to(message,"Пожалуйста напишите у кого убрать предупреждения")
    return
  users[str(message.reply_to_message.from_user.id)]["warnings"] = 0
  with open("users.json","w",encoding="UTF-8") as file:
    file.write(json.dumps(users,indent=4,ensure_ascii=False))
  await bot.send_message(message.from_user.id,f"Убраны все предупреждения")

@bot.message_handler(commands=["rang"])
async def userRang(message):
  if user(message):return
  await bot.delete_message(message.chat.id,message.message_id)
  if(message.reply_to_message == None):
    rang = users[str(message.from_user.id)]["rang"]
    score = users[str(message.from_user.id)]["score"]
    await bot.send_message(message.chat.id, f"*{message.from_user.username}*\n\nУровень: {rang} ({score}/25)")
  else:
    rang = users[str(message.reply_to_message.from_user.id)]["rang"]
    score = users[str(message.reply_to_message.from_user.id)]["score"]
    await bot.send_message(message.chat.id, f"*{message.reply_to_message.from_user.username}*\n\nУровень: {rang} ({score}/100)")

async def secret1(message):
  global users
  if user(message):return
  await bot.delete_message(message.chat.id,message.message_id)
  if message.chat.id == config["chat"] or users[str(message.from_user.id)]["secrets"][0]:return
  messages = []
  text = '''```cpp
#include <iostream>
using namespace std;

int main() 
{
    cout << "Я снова кричу тебе на всех языках";
    return 0;
}
  ```'''
  messages.append(await bot.send_message(message.chat.id,text))
  await asyncio.sleep(2)
  text = '''```c
#include <stdio.h>
 
int main()
{
  printf("Seni seviyorum\\n");
  return 0;
}
  ```'''
  messages.append(await bot.send_message(message.chat.id,text))
  await asyncio.sleep(2.5)
  text = '''```java
class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Я тебе кохаю");
    }
}
  ```'''
  messages.append(await bot.send_message(message.chat.id,text))
  await asyncio.sleep(2)
  text = '''```Pascal
program Hello;
begin
  writeln ('Te quiero')
end.
  ```'''
  messages.append(await bot.send_message(message.chat.id,text))
  await asyncio.sleep(2.5)
  text = '''```php
<?php
  echo "I love you";
?>
  ```'''
  messages.append(await bot.send_message(message.chat.id,text))
  await asyncio.sleep(1)
  text = '''```Assembler
.MODEL SMALL
.STACK 100h
.DATA
    HelloMessage DB 'I love you',13,10,'$'
.CODE
START:
    mov ax,@data
    mov ds,ax
    mov ah,9
    mov dx,OFFSET HelloMessage
    int 21h
    mov ah,4ch
    int 21h
END START
  ```'''
  messages.append(await bot.send_message(message.chat.id,text))
  await asyncio.sleep(1)
  text = '''```Scala
object HelloWorld {
  def main(args: Array[String]): Unit = {
    println("Мен сені сүйемін")
  }
}
  ```'''
  messages.append(await bot.send_message(message.chat.id,text))
  await asyncio.sleep(2.5)
  text = '''```javascript
alert("Я цябе кахаю");
  ```'''
  messages.append(await bot.send_message(message.chat.id,text))
  await asyncio.sleep(2)
  text = '''```csharp
using System;

namespace HelloWorld
{
    class Hello 
    {
        static void Main() 
        {
            Console.WriteLine("사랑해요");
        }
    }
}
  ```'''
  messages.append(await bot.send_message(message.chat.id,text))
  await asyncio.sleep(2.5)
  text = '''```python
print("Я тебя люблю!")
  ```'''
  messages.append(await bot.send_message(message.chat.id,text))
  await asyncio.sleep(1)
  messages.append(await bot.send_message(message.chat.id,"❤️"))
  await asyncio.sleep(3)
  for m in messages:
    await bot.delete_message(message.chat.id,m.message_id)
    await asyncio.sleep(0.1)
  await bot.send_message(message.chat.id,"Поздравляю! Вы нашли посхалку!")
  users[str(message.from_user.id)]["rang"]+=1
  users[str(message.from_user.id)]["secrets"][0] = True
  with open("users.json","w",encoding="UTF-8") as file:
    file.write(json.dumps(users,indent=4,ensure_ascii=False))
  
async def secret2(message):
  global users
  if user(message):return
  if message.chat.id == config["chat"] or users[str(message.from_user.id)]["secrets"][1]:
    await bot.delete_message(message.chat.id,message.message_id)
    return
  await asyncio.sleep(1.5)
  async with aiohttp.ClientSession() as session:
    tkn = config["token"]
    response = await session.get(f"https://api.telegram.org/bot{tkn}/sendPhoto?chat_id={message.chat.id}&photo=https://www.pluggedin.ru/images/1-bigTopImage_2023_10_17_12_29_52.jpg&caption=А я,")
    response_json = await response.json()
  message_id = response_json["result"]["message_id"]
  await asyncio.sleep(1.5)
  await bot.edit_message_caption("А я, так просто,",message.chat.id,message_id)
  await asyncio.sleep(1.5)
  await bot.edit_message_caption("А я, так просто, Железный человек!",message.chat.id,message_id)
  await asyncio.sleep(3)
  await bot.delete_message(message.chat.id,message_id)
  await bot.delete_message(message.chat.id,message.message_id)
  await asyncio.sleep(3)
  await bot.send_message(message.chat.id,"Поздравляю! Вы нашли посхалку!")
  users[str(message.from_user.id)]["rang"]+=1
  users[str(message.from_user.id)]["secrets"][1] = True
  with open("users.json","w",encoding="UTF-8") as file:
    file.write(json.dumps(users,indent=4,ensure_ascii=False))

@bot.message_handler(commands=["git"])
async def sendGit(message):
  await bot.send_message(message.chat.id,"https://github.com/AlekseevAndrew/TeleBot")

@bot.message_handler(commands=["homework"])
async def get_homework(message):
  if user(message):return
  global is_homework_updated, chat_messages_before_homework_get

  chat_messages_before_homework_get-=1
  if message.chat.id == config["chat"] and ((not is_homework_updated) and chat_messages_before_homework_get<=config["messages_before_get_homework"]):
    await bot.delete_message(message.chat.id,message.id)
    return

  get_hw()
  hw = "Дз:\n"
  for lesson in homework.items():
    hw += f"*{lesson[0]}* : {lesson[1]}\n" if lesson[1] != "`-`"  else ""
  is_homework_updated = False
  if message.chat.id == config["chat"]: chat_messages_before_homework_get = 0
  await bot.send_message(message.chat.id,hw.strip())

@bot.message_handler(commands=["photo"])
async def get_photo(message):
  if user(message):return
  await bot.delete_message(message.chat.id,message.message_id)

  if os.listdir("photos") == []:
    await bot.send_message(message.chat.id,"Нет(")
    return

  keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
  for i in os.listdir("photos"):
    keyboard.add(telebot.types.InlineKeyboardButton(i[:len(i)-3],callback_data=f"getPh/{i}"))
  keyboard.add(telebot.types.InlineKeyboardButton("-Отмена-",callback_data=f"getPh/exit"))

  await bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard)

@bot.message_handler(commands=["files"])
async def get_file(message):
  if user(message):return
  await bot.delete_message(message.chat.id,message.message_id)

  if os.listdir("documents") == []:
    await bot.send_message(message.chat.id,"Нет(")
    return

  keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
  for i in os.listdir("documents"):
    keyboard.add(telebot.types.InlineKeyboardButton(i[:len(i)-3],callback_data=f"getFile/{i}"))
  keyboard.add(telebot.types.InlineKeyboardButton("-Отмена-",callback_data=f"getFile/exit"))

  await bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard)

@bot.message_handler(commands=["set"])
async def set_homework(message):
  if user(message):return
  global homework
  global config
  global sets
  global timeout

  if not sets == None:
    if time()-timeout<=config["timeout"]:
      await bot.send_message(message.chat.id,"Извини я занята")
      await bot.send_message(sets[2],"Поторопись!")
      return
  timeout = time()
  if message.chat.id in config["moderators"]:
    sets=[None,None,message.chat.id]
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    for i in homework.keys():
      keyboard.add(telebot.types.InlineKeyboardButton(i,callback_data=f"sethw/{i}"))
    keyboard.add(telebot.types.InlineKeyboardButton("- Отмена -",callback_data=f"sethw/cancel"))
    await bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard)
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["schedule"])
async def getSchedule(message):
  if user(message):return
  global is_schedule_updated, chat_messages_before_schedule_get

  chat_messages_before_schedule_get-=1
  if message.chat.id == config["chat"] and ((not is_schedule_updated) and chat_messages_before_schedule_get<=config["messages_before_get_schedule"]):
    await bot.delete_message(message.chat.id,message.id)
    return
  
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
  if message.chat.id == config["chat"]: chat_messages_before_schedule_get = 0
  await bot.send_message(message.chat.id,res[:len(res)-1])

async def parseNetSchool(week=0):
    homeworks = {}
    ns = NetSchoolAPI(config["netSchool"]["link"])
    await ns.login(
        config["netSchool"]["login"],
        config["netSchool"]["password"],
        config["netSchool"]["school"]
    )
    st = datetime.date.today() - datetime.timedelta(datetime.date.today().weekday())
    start = st - datetime.timedelta(weeks=abs(week)) if week<0 else st + datetime.timedelta(weeks=week)
    end = start+ datetime.timedelta(days=5)

    diary = await ns.diary(start,end)
    schedule = diary.schedule
    for day in schedule:
        lessons = day.lessons
        for lesson in lessons:
            assignments=lesson.assignments
            for assignment in assignments:
                if assignment.type == "Домашнее задание":
                    homework = assignment.content
                    homeworks[lesson.subject] = homework

    diary = await ns.diary(start=start+ datetime.timedelta(weeks=1),end=end+ datetime.timedelta(weeks=1))
    schedule = diary.schedule
    for day in schedule:
        lessons = day.lessons
        for lesson in lessons:
            assignments=lesson.assignments
            for assignment in assignments:
                if assignment.type == "Домашнее задание":
                    homeworks[lesson.subject] = assignment.content

    await ns.logout()
    return homeworks

@bot.message_handler(commands=["netSchool"])
async def getNetschool(message):
  if user(message):return
  if not config["netSchool"]["enable"]:
    await bot.send_message(message.chat.id,"ОШИБКА: Данная функция отключена администраторм")
    return
  homeworks = await parseNetSchool()
  hw = "Дз:\n"
  for lesson in homeworks.items():
    hw += f"{lesson[0]} : {lesson[1]}\n" if lesson[1] != "-"  else ""
  await bot.send_message(message.chat.id,hw.strip())

@bot.message_handler(commands=["ban"])
async def add_to_black_list(message):
  if user(message):return
  if message.from_user.id in config["moderators"]:
    if message.reply_to_message == None: user_id = int(message.text.split()[1])
    else: user_id = message.reply_to_message.from_user.id
    if user_id == config["administrator"]:
      await bot.send_message(message.chat.id,"Нет, не буду я его банить!")
      return
    hours = int(message.text.split()[2])*3600+time()
    prichina = " ".join(message.text.split()[3:])
    if str(user_id) in users.keys():user_name = users[user_id]["username"]
    else: user_name = ""
    text = f'''
Пользователь {user_name} добавлен в чёрный список по причине:

"_{prichina}_"

Пользователь получит возможность вернуться в группу через {int(message.text.split()[2])} часов
По дополнительным вопросам обращатся к модераторам или администратору бота
'''
    
    if not user_id in blacklist:
      blacklist.append(user_id)
      set_blacklist()
    await bot.delete_message(message.chat.id,message.id)
    await bot.send_message(message.chat.id,text)
    await bot.ban_chat_member(config["chat"],user_id,hours)
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["unban"])
async def remove_user_from_black_list(message):
  if user(message):return
  if message.from_user.id in config["moderators"]:
    get_blacklist()
    user_id = int(message.text.split()[1])
    if user_id in blacklist:
      blacklist.remove(user_id)
    set_blacklist()
    await bot.send_message(message.chat.id,"👍")
    await bot.send_message(message.chat.id,"Готово!")
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["blacklist"])
async def send_blacklist(message):
  if user(message):return
  if message.chat.id in config["moderators"]:
    await bot.send_document(message.chat.id,telebot.types.InputFile("blacklist.json"))
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(content_types=["text",'animation', 'audio', 'photo', 'voice', 'video', 'video_note', 'document', 'sticker', 'location', 'contact'])
async def data_handler(message):

  global sets, homework, setc, config, setsh, schedule, sendf, lastMessages, is_homework_updated, event_creators
  global chat_messages_before_homework_get, is_schedule_updated, chat_messages_before_schedule_get, reminds
  if user(message):return
  Type = get_message_type(message)  

  if message.chat.id == config["chat"]:
    chat_messages_before_homework_get += 1
    chat_messages_before_schedule_get += 1
    users[str(message.from_user.id)]["score"]+=1
    if(users[str(message.from_user.id)]["score"]==25):
      users[str(message.from_user.id)]["score"]=0
      users[str(message.from_user.id)]["rang"]+=1
      rang = users[str(message.from_user.id)]["rang"]
      result = f"Поздравляю ты достиг {rang} уровня!"
      await bot.send_message(message.from_user.id,result)
      await bot.reply_to(message,result)
    with open("users.json","w",encoding="UTF-8") as file:
      file.write(json.dumps(users,indent=4,ensure_ascii=False))

  if (not sendf == None) and sendf[0] == message.chat.id:
    ID = sendf[1]
    if Type == "animation": await bot.send_animation(ID, message.animation.file_id)
    elif Type == "audio": await bot.send_audio(ID, message.audio.file_id)
    elif Type == "photo":
      photos = message.photo
      photos.reverse()
      await bot.send_photo(ID, photos[0].file_id, caption=message.caption)
    elif Type == "voice": await bot.send_voice(ID, message.voice.file_id)
    elif Type == "video": await bot.send_video(ID, message.video.file_id, caption=message.caption)
    elif Type == "video_note": await bot.send_video_note(ID, message.video_note.file_id)
    elif Type == "document": await bot.send_document(ID, message.document.file_id, caption=message.caption)
    elif Type == "sticker": await bot.send_sticker(ID, message.sticker.file_id)
    elif Type == "location": await bot.send_location(ID, message.location.latitude, message.location.longitude)
    elif Type == "contact": await bot.send_contact(ID, message.contact.phone_number, message.contact.first_name)
    await bot.send_message(message.chat.id,f"отправлено пользователю {ID}")
    sendf = None

  if not sets==None:
    if message.chat.id == sets[2] and (not sets[0] == None):
      if message.text == "Отмена":
        await bot.delete_message(message.chat.id,message.message_id)
        await bot.edit_message_text(chat_id=message.chat.id,message_id=sets[0].message_id,text="Отмена действия!")
        sets = None
      Lesson = sets[1]
      if Type=="photo":
        if not f"{Lesson}dir" in os.listdir("photos"): os.mkdir(f"photos/{Lesson}dir")
        p = len(os.listdir(f"photos/{Lesson}dir"))
        photo = message.photo[len(message.photo)-1]
        file_path = await bot.get_file(photo.file_id)
        file = await bot.download_file(file_path.file_path)
        with open(f"photos/{Lesson}dir/photo{p}.png", "wb") as code:
          code.write(file)
        await bot.send_message(message.chat.id,"Добавила!")
        if message.caption == "+":
          homework[sets[1]]="/photo"
          await bot.delete_message(message.chat.id,message.message_id)
          await bot.edit_message_text(chat_id=message.chat.id,message_id=sets[0].message_id,text="👍")
          await bot.send_message(message.chat.id,"Изменено!")
          is_homework_updated = True
          sets = None
          set_hw()
      elif Type == "document":
        if not f"{Lesson}dir" in os.listdir("documents"): os.mkdir(f"documents/{Lesson}dir")
        file_path = await bot.get_file(message.document.file_id)
        file = await bot.download_file(file_path.file_path)
        with open(f"documents/{Lesson}dir/{message.document.file_name}", "wb") as code:
          code.write(file)
        await bot.send_message(message.chat.id,"Добавила!")
      else:
        homework[sets[1]]=f"`{message.text}`" + (" /photo" if f"{Lesson}dir" in os.listdir("photos") else "") + (" /files" if f"{Lesson}dir" in os.listdir("documents") else "")
        await bot.delete_message(message.chat.id,message.message_id)
        await bot.edit_message_text(chat_id=message.chat.id,message_id=sets[0].message_id,text="👍")
        await bot.send_message(message.chat.id,"Изменено!")
        is_homework_updated = True
        sets = None
        set_hw()
      return
      
  if not setsh==None:
    if message.chat.id == setsh[2]:
      if setsh[3] == 0:
        st = int(message.text)
        setsh[5] = st
        setsh[3]=2
        await bot.edit_message_text(message_id=setsh[1],text=f"Сколько уроков?",chat_id=setsh[2])
        await bot.delete_message(message.chat.id,message.message_id)
      elif setsh[3] == 1:
        cab = (message.text)
        schedule.append({"name":setsh[0],"cab":cab})
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        les = len(schedule)-1
        for i in scheduleLessons:
          keyboard.add(telebot.types.InlineKeyboardButton(i,callback_data=f"setshl/{i}/{les}"))
        await bot.edit_message_text(message_id=setsh[1],text=f"Какой {les+1} урок?",chat_id=setsh[2],reply_markup=keyboard)
        await bot.delete_message(message.chat.id,message.message_id)
        if les == setsh[4]:
          await bot.edit_message_text(message_id=setsh[1],text=f"👍",chat_id=setsh[2])
          await bot.send_message(message.chat.id,"Изменено!")
          is_schedule_updated = True
          setsh = None
          set_sch()
      elif setsh[3] == 2:
        setsh[3]=1
        less = int(message.text)
        setsh[4] = less
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        for i in scheduleLessons:
          keyboard.add(telebot.types.InlineKeyboardButton(i,callback_data=f"setshl/{i}/0"))
        await bot.edit_message_text(message_id=setsh[1],text="Какой 1 урок?",chat_id=setsh[2],reply_markup=keyboard)
        await bot.delete_message(message.chat.id,message.message_id)
        schedule = [setsh[5]]
      return

  if str(message.chat.id) in reminders.keys():
    if len(reminders[str(message.chat.id)]) == 1:
      data = message.text.split()
      if len(data[0]) != 5:
        await bot.send_message(message.chat.id,"Пожалуйста используйте правильный формат!")
        return
      if len(data) != 1:
        try:
          days = list(map(int,data[1:]))
        except:
          await bot.send_message(message.chat.id,"Пожалуйста используйте правильный формат!")
          return
      else: days = []
      reminders[str(message.chat.id)].append(data[0])
      reminders[str(message.chat.id)].append(days)
      await bot.send_message(message.chat.id,"Что напомнить?")
      return
    if len(reminders[str(message.chat.id)]) == 3:
      get_reminds()
      reminder = reminders[str(message.chat.id)]
      remind = {
        "user":reminder[0],
        "text":message.text,
        "date":reminder[1],
        "days":reminder[2]
      }
      reminds.append(remind)
      set_reminds()
      del reminders[str(message.chat.id)]
      days_str = ", ".join(list(map(str,remind["days"])))
      date = remind["date"]
      await bot.send_message(message.chat.id,f"Хорошо! Напомню '{message.text}' В дату {date}"+(f" и за {days_str} дней." if days_str!="" else ""))
      return
  
  if str(message.chat.id) in event_creators.keys():
    event_creator = event_creators[str(message.chat.id)]
    if len(event_creator) == 1:
      event_creators[str(message.chat.id)].append(message.text)
      await bot.send_message(message.chat.id,"Теперь если нужно отправте изображения, а затем текст обьявления")
    elif len(event_creator) == 2:
      dir = "events/"+event_creator[0]
      if Type=="photo":
        p = len(os.listdir(dir))
        photo = message.photo[len(message.photo)-1]
        file_path = await bot.get_file(photo.file_id)
        file = await bot.download_file(file_path.file_path)
        with open(f"{dir}/photo{p}.png", "wb") as code:
          code.write(file)
        await bot.send_message(message.chat.id,"Добавила!")
        if message.caption == "+":
          event_data = {
            "name": event_creator[1],
            "text": ""
          }
          with open(f"{dir}/event_data.json","w",encoding="UTF-8") as f:
            f.write(json.dumps(event_data,ensure_ascii=False,indent=4))
          await bot.send_message(message.chat.id,"Создано!")
          del event_creators[str(message.chat.id)]
      else:
        event_data = {
          "name": event_creator[1],
          "text": message.text
        }
        with open(f"{dir}/event_data.json","w",encoding="UTF-8") as f:
          f.write(json.dumps(event_data,ensure_ascii=False,indent=4))
        await bot.send_message(message.chat.id,"Создано!")
        del event_creators[str(message.chat.id)]
      return

  if Type == "text":
    if "!шар" in message.text: await ball(message=message)
    if "!пред" in message.text: await sendWarning(message=message)
    if message.text == "!ранг": await userRang(message=message)
    if message.text.lower() == None and message.caption == None: return
    if message.text.lower() in config["user_commands"]["getHomeworkCommands"]:await get_homework(message=message)
    if message.text.lower() in config["user_commands"]["getScheduleCommands"]:await getSchedule(message=message)
    if message.text.lower() in config["user_commands"]["getPhotosCommands"]:await get_photo(message=message)
    if message.text.lower() in config["user_commands"]["getFilesCommands"]:await get_file(message=message)
    if config["netSchool"]["enable"] and message.text.lower() in config["netSchool"]["getNetSchoolHomeworkCommands"]: await getNetschool(message=message)
    if config["dnevnik_egov66"]["enable"] and message.text.lower() in config["dnevnik_egov66"]["getHomeworkCommands"]: await getDnevnikEgov66(message=message)
    if message.text.lower() in config["user_commands"]["GetEventsCommands"]:await get_events(message=message)
    if message.chat.id in config["moderators"]:
      if message.text.lower() in config["moderatorCommands"]["SetScheduleCommands"]:await setSchedule(message=message)
      if message.text.lower() in config["moderatorCommands"]["SetHomeworkCommands"]:await set_homework(message=message)
      if message.text.lower() in config["moderatorCommands"]["CreateEventCommands"]:await create_event(message=message)
      if message.text.lower() in config["moderatorCommands"]["DeleteEventCommands"]:await delete_event(message=message)

    if message.chat.id == config["administrator"]:
      if message.text.lower() in config["administratorCommands"]["getUsersCommands"]:await usersLog(message=message)
      if message.text.lower() in config["administratorCommands"]["getLogCommands"]:await printLog(message=message)
      if message.text.lower() in config["administratorCommands"]["getConfigCommands"]:await get_config(message=message)
      if message.text.lower() in config["administratorCommands"]["getBlackListCommands"]:await send_blacklist(message=message)

    if message.from_user.id in config["moderators"] and message.chat.id == config["chat"]:
      if message.text.lower() in config["moderatorCommands"]["PinMessageCommands"]: await pin_message(message=message)
      if message.text.lower() in config["moderatorCommands"]["UnpinMessageCommands"]: await unpin_message(message=message)
      if message.text.lower() in config["moderatorCommands"]["UnpinMessagesCommands"]: await unpin_all_messages(message=message)

    if message.chat.id != config["chat"]:
      if message.text == "❤️":await secret1(message=message) # Посхалка
      if message.text == "Я сома неотвратимость":await secret2(message=message) # Посхалка  
      if message.text.lower() in config["user_commands"]["CreateRemindCommands"]:await create_remind(message=message)
      if message.text.lower() in config["user_commands"]["ListRemindsCommands"]:await list_reminds(message=message)
      if message.text.lower() in config["user_commands"]["DeleteRemindCommands"]:await delete_remind(message=message)
      if message.chat.id in config["moderators"]:
        if message.text.lower() in config["moderatorCommands"]["CreateClassRemindCommands"]: await create_remind_for_all(message=message)
        if message.text.lower() in config["moderatorCommands"]["ListClassRemindsCommands"]: await list_reminds_for_all(message=message)
        if message.text.lower() in config["moderatorCommands"]["DeleteClassRemindCommands"]: await delete_remind_for_all(message=message)

    if message.chat.id == config["chat"] and message.from_user.id in config["moderators"]:
      lastMessages[message.from_user.id] = message.id

@bot.callback_query_handler(lambda call: True)
async def keyboard(call):
  global sets, setc, setsh, reminds, homework

  if call.message:
    data = call.data.split("/")
    if data[0] == "sethw":
      if data[1] == "cancel":
        sets = None
        await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="Отмена действия!")
        return
      sets = [call.message,data[1],call.message.chat.id]
      if data[1]+"dir" in os.listdir("photos"):
        shutil.rmtree(f"photos/{data[1]}dir")
      if data[1]+"dir" in os.listdir("documents"):
        shutil.rmtree(f"documents/{data[1]}dir")
      keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
      keyboard.add(telebot.types.InlineKeyboardButton("- Отмена -",callback_data=f"sethw/cancel"))
      await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=data[1],reply_markup=keyboard)

    if data[0] == "delhwl":
      del homework[data[1]]
      set_hw()
      await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="👍")
      await bot.send_message(call.message.chat.id,"Готово!")

    if data[0] == "setshl":
      setsh[0]  = data[1]
      await bot.edit_message_text(message_id=setsh[1],text="Какой кбинет?",chat_id=setsh[2])

    if data[0] == "delshl":
      scheduleLessons.remove(data[1])
      set_schl()
      await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="👍")
      await bot.send_message(call.message.chat.id,"Готово!")

    if data[0] == "getPh":
      l = data[1]
      await bot.delete_message(call.message.chat.id,call.message.message_id)
      phsfs =[]
      if l == "exit":return
      for i in os.listdir(f"photos/{l}"):
        phsfs.append(telebot.types.InputMediaPhoto(media=open(f"photos/{l}/{i}","rb"),caption=(l[:len(l)-3] if i == "photo0.png" else None)))
      await bot.send_media_group(call.message.chat.id,phsfs)

    if data[0] == "delete_remind":
      if data[1] == "cancel":
        await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="Отмена действия!")
        return
      elif data[1] == "all":
        to_r = []
        for remind in reminds:
          if remind["user"] == call.message.chat.id:
            to_r.append(remind)
        for tor in to_r:
          reminds.remove(tor)
        await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=f"Удалено {len(to_r)} напоминаний!")
      else:
        reminds.pop(int(data[1]))
        await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=f"Удалено!")
      set_reminds()

    if data[0] == "delete_remind_for_all":
      if data[1] == "cancel":
        await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="Отмена действия!")
        return
      elif data[1] == "all":
        to_r = []
        for remind in reminds:
          if remind["user"] == config["chat"]:
            to_r.append(remind)
        for tor in to_r:
          reminds.remove(tor)
        await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=f"Удалено {len(to_r)} напоминаний!")
      else:
        reminds.pop(int(data[1]))
        await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=f"Удалено!")
      set_reminds()

    if data[0] == "get_event":
      if data[1] == "close":
        await bot.delete_message(call.message.chat.id,call.message.message_id)
        return
      dir = data[1]
      with open(f"events/{dir}/event_data.json",encoding="UTF_8") as f:
        event_data = json.loads(f.read())
      name = event_data["name"]
      text = event_data["text"]
      res = f"*{name}*" + (f" \n\n {text}" if text != "" else "")
      listdir = os.listdir(f"events/{dir}")
      if len(listdir) == 1:
        await bot.send_message(call.message.chat.id,res)
      else:
        l = data[1]
        phsfs =[]
        if l == "exit":return
        for i in os.listdir(f"events/{dir}"):
          if i == "event_data.json":continue
          phsfs.append(telebot.types.InputMediaPhoto(media=open(f"events/{dir}/{i}","rb"),caption=(res if i == "photo0.png" else None)))
        await bot.send_media_group(call.message.chat.id,phsfs)
      await bot.delete_message(call.message.chat.id,call.message.message_id)

    if data[0] == "delete_event":
      if data[1] == "all":
        for dir in os.listdir("events"):
          shutil.rmtree(f"events\\{dir}")
        await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="Удалены все объявления!")
        return
      elif data[1] == "close":
        await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="Отмена действия!")
        return
      dir = data[1]
      shutil.rmtree(f"events\\{dir}")
      await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="Удалено!")

    if data[0] == "dnevnikEgov66":
      if data[1] == "close":
        await bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
        return
      day = int(data[1])
      key = telebot.types.InlineKeyboardMarkup(row_width=4)
      key.add(telebot.types.InlineKeyboardButton("<3",callback_data=f"dnevnikEgov66/{day-3}"),
              telebot.types.InlineKeyboardButton("<",callback_data=f"dnevnikEgov66/{day-1}"),
              telebot.types.InlineKeyboardButton(">",callback_data=f"dnevnikEgov66/{day+1}"),
              telebot.types.InlineKeyboardButton("3>",callback_data=f"dnevnikEgov66/{day+3}"),
              telebot.types.InlineKeyboardButton("<7",callback_data=f"dnevnikEgov66/{day-7}"),
              telebot.types.InlineKeyboardButton("<5",callback_data=f"dnevnikEgov66/{day-5}"),
              telebot.types.InlineKeyboardButton("5>",callback_data=f"dnevnikEgov66/{day+5}"),
              telebot.types.InlineKeyboardButton("7>",callback_data=f"dnevnikEgov66/{day+7}"))
      hw_raw = await dnevnikEgov66.getDayHomework(day)
      date = hw_raw["date"]
      hw = f"*{date}*\n\n"
      for i,lesson in enumerate(hw_raw["homework"]):
        name = lesson["name"]
        text = lesson["text"]
        hw += f"*{name}*\n`{text}`\n\n"
        if lesson["files"] != []:key.add(telebot.types.InlineKeyboardButton(f"*[{i}] {name}*",callback_data=f"dnevnikEgov66download/{date}/{i}"))
      if call.message.chat.id in config["moderators"]:key.add(telebot.types.InlineKeyboardButton("- Записать -",callback_data=f"dnevnikEgov66toBase/0/{date}"))
      key.add(telebot.types.InlineKeyboardButton("- Закрыть -",callback_data="dnevnikEgov66/close"))
      await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=hw,reply_markup=key)

  if data[0] == "dnevnikEgov66download":
    date = data[1]
    index = int(data[2])
    hw_raw = await dnevnikEgov66.getDateHomework(date)
    hw_lesson_files = hw_raw["homework"][index]["files"]
    lesson_name = hw_raw["homework"][index]["name"]
    for file in hw_lesson_files:
      fileo = await dnevnikEgov66.getFile(file["id"])
      obj = BytesIO(fileo)
      obj.name = file["name"]
      await bot.send_document(call.message.chat.id, obj, caption=f"`{date}` *{lesson_name}*")

  if data[0] == "dnevnikEgov66toBase":
    index = int(data[1])
    date = data[2]
    if index == 0:
      hw_raw = await dnevnikEgov66.getDateHomework(date)
      hw_lessons = hw_raw["homework"]
      key = telebot.types.InlineKeyboardMarkup()
      for i,lesson in enumerate(hw_lessons):
        name = lesson["name"]
        key.add(telebot.types.InlineKeyboardButton(f"*{name}*",callback_data=f"dnevnikEgov66toBase/1/{date}/{i}"))
      await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="Из какого предмета?",reply_markup=key)
    elif index == 1:
      li = data[3]
      key = telebot.types.InlineKeyboardMarkup()
      for i,lesson in enumerate(homework.keys()):
        key.add(telebot.types.InlineKeyboardButton(f"*{lesson}*",callback_data=f"dnevnikEgov66toBase/2/{date}/{li}/{i}"))
      await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="В какой предмет?",reply_markup=key)
    elif index == 2:
      hw_raw = await dnevnikEgov66.getDateHomework(date)
      hw_lesson = hw_raw["homework"][int(data[3])]
      lesson_name = list(homework.keys())[int(data[4])]
      if lesson_name+"dir" in os.listdir("documents"):
        shutil.rmtree(f"documents/{lesson_name}dir")
      if hw_lesson["files"] != []:os.mkdir(f"documents/{lesson_name}dir")
      for file in hw_lesson["files"]:
        file_name = file["name"]
        async with aiofiles.open(f"documents/{lesson_name}dir/{file_name}","wb") as f:
          await f.write(await dnevnikEgov66.getFile(file["id"]))
      text = hw_lesson["text"]
      homework[lesson_name] = f"`{text}`" + (" /files" if f"{lesson_name}dir" in os.listdir("documents") else "")
      await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="👍")
      await bot.send_message(call.message.chat.id,"Готово!")
      set_hw()

  if data[0] == "getFile":
      l = data[1]
      await bot.delete_message(call.message.chat.id,call.message.message_id)
      if l == "exit":return
      for i in os.listdir(f"documents/{l}"):
        async with aiofiles.open(f"documents/{l}/{i}","rb") as f:
          fileo = await f.read()
          obj = BytesIO(fileo)
          obj.name = i
          lesson_name = l[:len(l)-3]
          await bot.send_document(call.message.chat.id, obj, caption=f"*{lesson_name}*")
      
old_date = datetime.datetime.now() - datetime.timedelta(days=1)

async def tick():
  global old_date, reminds
  date = datetime.datetime.now()
  if old_date.day != date.day and date.hour>=config["tickHour"]:
    old_date = date
    dm = ("0" if len(str(date.day))==1 else "")+str(date.day)
    m = ("0" if len(str(date.month))==1 else "")+str(date.month)
    d = f"{dm}.{m}"
    tomorow = date + datetime.timedelta(days=1)
    mt = ("0" if len(str(tomorow.month))==1 else "")+str(tomorow.month)
    dmt = ("0" if len(str(tomorow.day))==1 else "")+str(tomorow.day)
    dt = f"{dmt}.{mt}"
    with open("birthdays.json",encoding="UTF-8") as f:
      birthdays = json.loads(f.read())
    for birthday in birthdays:
      name = birthday["name"]
      if birthday["date"] == dt:
        await bot.send_message(config["birthdayAdministrator"],f"Здравствуйте, напоминаю что завтра день рождения у *{name}*!")
      if birthday["date"] == d:
        await bot.send_message(config["chat"],f"Сегодня день рождения у *{name}*! Поздравляем!!!")
        await bot.send_message(config["birthdayAdministrator"],f"Здравствуйте, напоминаю что сегодня день рождения у *{name}*!")

    get_reminds()
    if reminds != []:
      remindsToRemove = []
      for i,remind in enumerate(reminds):
        text = remind["text"]
        if d == remind["date"]:
          await bot.send_message(remind["user"],f"Напоминаю! *{text}*!")
          remindsToRemove.append(i)
        else:
          for day in remind["days"]:
            date_tomorow = date + datetime.timedelta(days=day)
            dmd = ("0" if len(str(date_tomorow.day))==1 else "")+str(date_tomorow.day)
            md = ("0" if len(str(date_tomorow.month))==1 else "")+str(date_tomorow.month)
            dd = f"{dmd}.{md}"
            if dd == remind["date"]:
              await bot.send_message(remind["user"],f"Напоминаю через {day} дня! *{text}*!")
              break
      for i,index in enumerate(remindsToRemove):reminds.pop(index-i)
      set_reminds()

bot.programm_tick_function = tick
asyncio.run(bot.polling(non_stop=True))