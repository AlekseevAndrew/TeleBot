# Telebot

Telebot - это телеграм бот созданный для помощи школьным классам.
Он способен сообщать домашнее задание, расписание и поздровлять с днём рождения
#### На самом деле имя бота Наташа

## Требования

 * Python 3.9+
 * Постоянно активный сервер с доступом в интернет
 * Linux или Windows

## Установка и настройка
 
 * Создайте бота в телеграм (подробнее в [`Как создать бота в телеграм`](Readme/CreateBot.md))
 * `pip install -r reqarements.txt`
 * Создайте файл [`config.json`](Readme/config.json) в папке бота
 * Создайте файл [`birthdays.json`](Readme/birthdays.json) в папке бота

## Использование

После установки и настройки ничего сложного в запуске нет! Достаточно перейти в корневую папку бота и написать одну команду:
 * Для Windows 
 ```
 python main.py
 ```

 * Для Linux 
 ```
 python3 main.py
 ```

 ### Команды

 Все команды есть в [`Команды бота`](Readme/help.md)

 После отправки команды `/start` у вас появятся кнопки которые позволяют удобно получать ДЗ, Расписание и фото к ДЗ