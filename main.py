import os
import telebot as telebot
import json
import shutil
import datetime
import asyncio
from netschoolapi import NetSchoolAPI
from time import time
from telebot import async_telebot

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
photos = []

if not "users.json" in os.listdir():
  with open("users.json","w",encoding="UTF-8") as file:
    file.write("{}")

def init():
  global users, helpText, config, homework, schedule, scheduleLessons, photos

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

bot=async_telebot.AsyncTeleBot(config["token"],parse_mode="markdown")

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
  else: return "text"

@bot.message_handler(commands=['start'])
async def start_message(message):
  key = telebot.types.ReplyKeyboardMarkup(True)
  key.add(telebot.types.KeyboardButton(config["getHomeworkCommands"][0]),telebot.types.KeyboardButton(config["getScheduleCommands"][0]),telebot.types.KeyboardButton(config["getPhotosCommands"][0]))
  if config["netSchool"]["enable"]:key.add(telebot.types.KeyboardButton(config["netSchool"]['getNetSchoolHomeworkCommands'][0]))
  if message.chat.id in config["moderators"]:key.add(config["moderatorCommands"]["SetScheduleCommands"][0],config["moderatorCommands"]["SetHomeworkCommands"][0])
  if message.chat.id == config["administrator"]:key.add(config["administratorCommands"]["getLogCommands"][0],config["administratorCommands"]["getUsersCommands"][0])
  await bot.send_message(message.chat.id,f"Привет ✌️ {message.from_user.first_name}",reply_markup=key)

@bot.message_handler(commands=["addLesson"])
async def addLesson(message):
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
  if message.chat.id in config["moderators"]:
    get_hw()
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    for i in homework.keys():
      keyboard.add(telebot.types.InlineKeyboardButton(i,callback_data=f"delhwl/{i}"))

    await bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard)
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["addSLesson"])
async def addLesson(message):
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
  if message.chat.id in config["moderators"]:
    get_schl()
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    for i in scheduleLessons:
      keyboard.add(telebot.types.InlineKeyboardButton(i,callback_data=f"delshl/{i}"))

    await bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard)
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["setSchedule"])
async def setSchedule(message):
  global setsh
  if message.chat.id in config["moderators"]:
    m = await bot.send_message(message.chat.id,"С какого урока?")
    setsh=[{},m.message_id,message.chat.id,0,0,0]
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["sendText"])
async def text(message):
  txt = message.text.split()
  await bot.send_message(convertId(txt[1])," ".join(txt[2:len(txt)]))

@bot.message_handler(commands=["log"])
async def printLog(message):
  if message.chat.id in config["moderators"]:
    with open("messages.log") as f:
      if f.read()=="":
        await bot.send_message(message.chat.id,"Логи пусты!")
        return
    await bot.send_document(message.chat.id,telebot.types.InputFile("messages.log"))
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["clearLog"])
async def clearLog(message):
  if message.chat.id==config["administrator"]:
    with open("messages.log","w") as file:file.write("")
    await bot.send_message(message.chat.id,"Отчистила логи.")
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["version"])
async def version(message):
  await bot.send_message(message.chat.id,str(config["version"]))

@bot.message_handler(commands=["users"])
async def usersLog(message):
  if message.chat.id==config["administrator"]:
    with open("users.json") as f:
      if f.read()=="":
        await bot.send_message(message.chat.id,"пусто")
        return
    await bot.send_document(message.chat.id,telebot.types.InputFile("users.json"))
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["config"])
async def shutdown(message):
  global config
  if message.chat.id==config["administrator"]:
    with open("config.json") as f:
      if f.read()=="":
        await bot.send_message(message.chat.id,"пусто")
        return
    await bot.send_document(message.chat.id,telebot.types.InputFile("config.json"))
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["raise"])
async def shutdown(message):
  global config
  if message.chat.id==config["administrator"]:
    exit()
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["setconfig"])
async def setconfig(message):
  global config
  if message.chat.id==config["administrator"]:
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    for i in config.keys():
      keyboard.add(telebot.types.InlineKeyboardButton(i,callback_data=f"setc/{i}"))
    await bot.send_message(message.chat.id,"Настройка",reply_markup=keyboard)
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["help"])
async def help(message):
  global helpText
  await bot.send_message(message.chat.id,helpText)

@bot.message_handler(commands=["id"])
async def get_my_id(message):
  await bot.send_message(message.chat.id,message.chat.id)

@bot.message_handler(commands=["reload"])
async def reload_sys(message):
  global config
  if message.chat.id==config["administrator"]:
    await bot.send_message(message.chat.id,"Перезагрузка!")
    bot.stop_polling()
    os.system(config["startCommand"])
    exit()
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["reinit"])
async def reload_sys(message):
  global config
  if message.chat.id==config["administrator"]:
    await bot.send_message(message.chat.id,"Инициализация!")
    init()
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["sendFile"])
async def sendFile(message):
  global sendf
  sendf = [message.chat.id,convertId(message.text.split()[1])]
  await bot.send_message(message.chat.id,f"что отправить пользователю {message.text.split()[1]}?")

@bot.message_handler(commands=["homework"])
async def get_homework(message):
  global homework

  get_hw()
  hw = "Дз:\n"
  for lesson in homework.items():
    hw += f"{lesson[0]} : {lesson[1]}\n" if lesson[1] != "-"  else ""
  await bot.send_message(message.chat.id,hw.strip())

@bot.message_handler(commands=["photo"])
async def get_photo(message):
  await bot.delete_message(message.chat.id,message.message_id)

  if os.listdir("photos") == []:
    await bot.send_message(message.chat.id,"Нету(")
    return

  keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
  for i in os.listdir("photos"):
    keyboard.add(telebot.types.InlineKeyboardButton(i[:len(i)-3],callback_data=f"getPh/{i}"))

  await bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard)

@bot.message_handler(commands=["set"])
async def set_homework(message):
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

    await bot.send_message(message.chat.id,"По какому?",reply_markup=keyboard)
  else:await bot.send_message(message.chat.id,"ОШИБКА: ОТКАЗАНО В ДОСТУПЕ!")

@bot.message_handler(commands=["schedule"])
async def getSchedule(message):
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
  if not config["netSchool"]["enable"]:
    await bot.send_message(message.chat.id,"ОШИБКА: Данная функция отключена администраторм")
    return
  homeworks = await parseNetSchool()
  hw = "Дз:\n"
  for lesson in homeworks.items():
    hw += f"{lesson[0]} : {lesson[1]}\n" if lesson[1] != "-"  else ""
  await bot.send_message(message.chat.id,hw.strip())

@bot.message_handler(content_types=["text",'animation', 'audio', 'photo', 'voice', 'video', 'video_note', 'document', 'sticker', 'location', 'contact'])
async def data(message):
  global sets, homework, setc, config, setsh, schedule, sendf
  user(message)
  Type = get_message_type(message)  
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

  if message.text == None and message.caption == None: return
  log(f"{message.chat.id}/{message.from_user.id}:{message.text}")
  if message.text in config["getHomeworkCommands"]:await get_homework(message=message)
  if message.text in config["getScheduleCommands"]:await getSchedule(message=message)
  if message.text in config["getPhotosCommands"]:await get_photo(message=message)
  if config["netSchool"]["enable"] and message.text in config["netSchool"]["getNetSchoolHomeworkCommands"]: await getNetschool(message=message)
  if message.chat.id in config["moderators"]:
    if message.text in config["moderatorCommands"]["SetScheduleCommands"]:
      await setSchedule(message=message)
      return
    if message.text in config["moderatorCommands"]["SetHomeworkCommands"]:await set_homework(message=message)
  if message.chat.id == config["administrator"]:
    if message.text in config["administratorCommands"]["getUsersCommands"]:await usersLog(message=message)
    if message.text in config["administratorCommands"]["getLogCommands"]:await printLog(message=message)

  if not sets==None:
    if message.chat.id == sets[2] and (not sets[0] == None):
      Lesson = sets[1]
      if Type=="photo" and message.caption == "+":
        if not f"{Lesson}dir" in os.listdir("photos"): os.mkdir(f"photos/{Lesson}dir")
        p = len(os.listdir(f"photos/{Lesson}dir"))
        photo = message.photo[len(message.photo)-1]
        file_path = await bot.get_file(photo.file_id)
        file = await bot.download_file(file_path.file_path)
        with open(f"photos/{Lesson}dir/photo{p}.png", "wb") as code:
          code.write(file)
        await bot.send_message(message.chat.id,"Добавила!")
        return
      else:
        homework[sets[1]]=message.text + (" /photo" if f"{Lesson}dir" in os.listdir("photos") else "")
      await bot.delete_message(message.chat.id,message.message_id)
      await bot.edit_message_text(chat_id=message.chat.id,message_id=sets[0].message_id,text="👍")
      await bot.send_message(message.chat.id,"Изменено!")
      sets = None
      set_hw()

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

  if message.chat.id == config["administrator"]:
    if not setc==None:
      config[setc]=eval(message.text)
      with open("config.json","w",encoding="UTF-8") as f:
        f.write(json.dumps(config,indent=4,ensure_ascii=False))
      await bot.delete_message(message.chat.id,message.message_id)
      await bot.send_message(message.chat.id,"👍")
      await bot.send_message(message.chat.id,"Изменено!")

@bot.callback_query_handler(lambda call: True)
async def keyboard(call):
  global sets,setc,setsh

  if call.message:
    data = call.data.split("/")
    if data[0] == "sethw":
      sets = [call.message,data[1],call.message.chat.id]
      if data[1]+"dir" in os.listdir("photos"):
        shutil.rmtree(f"photos/{data[1]}dir")
      await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=data[1])
    if data[0] == "setc":
      setc = data[1]
      await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=config[data[1]])
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
      for i in os.listdir(f"photos/{l}"):
        phsfs.append(telebot.types.InputMediaPhoto(media=open(f"photos/{l}/{i}","rb"),caption=(l[:len(l)-3] if i == "photo0.png" else None)))
      await bot.send_media_group(call.message.chat.id,phsfs)

old_date = datetime.datetime.now() - datetime.timedelta(days=1)

async def tick():
  global old_date
  date = datetime.datetime.now()
  if date.hour>=config["birthdayHour"] and old_date.day != date.day:
    old_date = date
    dm = ("0" if len(str(date.day))==1 else "")+str(date.day)
    m = ("0" if len(str(date.month))==1 else "")+str(date.month)
    d = f"{dm}.{m}"
    tomorow = datetime.datetime.now() + datetime.timedelta(days=1)
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

bot.programm_tick_function = tick
asyncio.run(bot.polling(non_stop=True))