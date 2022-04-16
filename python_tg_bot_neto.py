import telebot
import re
from random import choice

import os
from dotenv import load_dotenv

import json
from datetime import datetime
import time

from telebot import types


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
#print(dotenv_path)

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

token =   os.environ.get('token')

bot = telebot.TeleBot(token)



dictionary = {
    'greet': ['#NAME#, здравствуйте!', '#NAME#, добрый день!', '#NAME#, доброго дня!'],
    'thank': ['Спасибо за выполненное домашнее задание к блоку *#BLOCK#*!', 'Благодарю, что выполнили домашнее задание к блоку *#BLOCK#*!',
        'Здорово, что Вы сделали домашнее задание к блоку *#BLOCK#*!',
        'Здорово, что Вы выполнили домашнее задание к блоку *#BLOCK#*!',
        'Благодарим за выполнение домашнего задания к блоку *#BLOCK#*!',
        'Благодарю за выполненную работу к блоку *#BLOCK#*!'
    ],
    'success': ['Вы удачно реализовали …',
        'Отмечу, что получилось …',
        'Вам отлично удалось выполнить…',
        'У Вас отлично получилось ...',
        'Вам удалось ...',
        'Здорово, что вы посмотрели на проблему так-то…  и это позволило…'

        ],
    'improve': ['Хочу обратить ваше внимание на …',
         'Обратите внимание, что …',
         'Как специалист хочу предостеречь вас  от …',
         'Будьте внимательны - …',
         'Примите, пожалуйста, во внимание, что …',
         'В дальнейшем вы можете…',
         'Также советую обратить внимание на…'
         ],
    'result_good': [
            'Желаю удачи в воплощении вашего проекта!',
            'Удачи в дальнейшем обучении!',
            'Продолжайте в том же духе!',
            'Зачет!',
            'Вы проделали отличную работу!'
        ],
    'result_neg': [
            'Пожалуйста, внесите исправления в решение.',
            'Исправьте, пожалуйста, замечания, указанные выше.',
            'Пожалуйста, выполните исправления.',
            'Пожалуйста, доработайте свое решение.',
            'Пока работа требует доработки. ',
            'Внесите, пожалуйста, правки.'
        ]
    }


commands = {
    #'add' : {'descr' : 'add '},
    'help' : {'descr' : 'This command shows help.'},
    'answer': {'descr': 'This command creates an answer. It needs arguments in square braces.', 'args': [
        {'code': 'NAME', 'name': 'Имя слушателя', 'type': 'string'},
        {'code': 'BLOCK', 'name': 'Название блока', 'type': 'string'},
        {'code': 'SUCCESS', 'name': 'Решение принято? Y = Да, N = Нет', 'type': 'boolean'},
        ],
        'example': '/answer [Петр] [Базовые функции PHP] [Y]'
    }
}

#dictionaryStr = json.JSONEncoder().encode(dictionary)
#commandsStr = json.JSONEncoder().encode(commands)

#print(dictionaryStr, commandsStr)

#dictionary = os.environ.get('dictionary')
#commands = os.environ.get('commands')

data_folder = "bot_data"

def extractHistory(str = '{}'):
    try:
        h = json.JSONDecoder().decode(str)
    except Error:
        h = {}
    return h

def addHistory(f, history):
    f.write(json.JSONEncoder().encode(history))

def hist(userId, txt):

    markup = None

    ans = ''
    lastCode = ''
    isCommand = False
    if(txt[0] == '/'):
        isCommand = True

    global data_folder

    user_folder = data_folder + f'/{userId}'
    if not os.path.isdir(user_folder):
        os.makedirs(user_folder)

    path = user_folder + '/history.json'
    print('path', path)

    historyStr = ''
    try:
        f = open(path, 'r')
        historyStr = f.read()
        f.close()
    except FileNotFoundError:
        if(isCommand == False):
            return 'Enter command', None

    print('historyStr', historyStr)

    #os.remove(path)

    if(len(historyStr) == 0):
        history = extractHistory()
    else:
        history = extractHistory(historyStr)
    print('history', history)

    command = commands['answer']
    k = 0
    for i in range(0, len(command['args'])):
        code =  command['args'][i]['code']
        if(code not in history):
            history[code] = None
            ans = 'Введите *' + command['args'][i]['name'] + '*'
            lastCode = code
            break
        else:
            if history[code] == None:
                if not isCommand:
                    k += 1
                    history[code] = txt
                else:
                    ans = 'Введите *' + command['args'][i]['name'] + '*'
                    lastCode = code
                    break
            else:
                k +=1

    if(k == len(command['args'])):
        #генерим
        success = history['SUCCESS'] == 'Y'
        for key in dictionary:
            #print(key)
            part = choice(dictionary[key])

            if(success and key == 'result_neg' or not success and key == 'result_good'):
                continue;

            for i in history:
                repl = ''
                if(history[i] is not None):
                    repl = history[i]
                part = part.replace(f'#{i}#', repl)

            ans += part+ '\n\n'

        os.remove(path)

    else:
        print(k)
        print(history)
        f = open(path, 'w+')
        f.write(json.JSONEncoder().encode(history))
        f.close()

    if(len(ans) == 0):
        ans = 'I dont\'t understand you'

    if lastCode == 'SUCCESS':
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('Y')
        itembtn2 = types.KeyboardButton('N')
        markup.add(itembtn1, itembtn2)
    else:
        markup = None

    return ans, markup


@bot.message_handler(commands=['help'])
def help(message):
    help = '';
    for cmd in commands:
        command = commands[cmd]
        #print(command)

        if('descr' in command):
            descr = command['descr']
            help = help + "/" + cmd + ' - ' + descr + '\n'
        else:
            help = help + "/" + cmd  + '\n'

        if('args' in command):
            args= command['args']
            if(args is not None):
                for i in range(0, len(args)):
                    help += args[i]['name'] + ': ' + args[i]['type'] + '\n'


    bot.send_message(message.chat.id, help)

@bot.message_handler(commands=['answer'])
@bot.message_handler()
def help(message):
    #print(message)

    userId = message.from_user.id

    ans, markup = hist(userId, message.text)



    bot.reply_to(message, ans, parse_mode='Markdown', reply_markup=markup)


other_commands = []
for cmd in commands:
    if(cmd != 'help' and cmd != 'answer'):
        other_commands.append(cmd)


@bot.message_handler(commands=other_commands)
def other(message):
    #bot.send_message(message.chat.id, message.text)
    #print(message)

    msg = ''


    if(len(msg) > 0):
        bot.send_message(message.chat.id, msg)



bot.polling(none_stop=True)
