import telebot
import re
from random import choice

import os
from dotenv import load_dotenv

import json
from datetime import datetime
import time

from telebot import types

import logging

import pymongo
from pymongo import MongoClient, InsertOne, UpdateOne

from bson.json_util import loads


class Env:
    token = None
    dbClient = None

    def __init__(self):

        logging.basicConfig(filename='app.txt', filemode='r', format='%(name)s - %(levelname)s - %(message)s')
        self.getEnv()


    def getEnv(self):

        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        #print(dotenv_path)

        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)


        dbLogin = os.environ.get('dbLogin')
        dbPassword = os.environ.get('dbPassword')
        dbPath = os.environ.get('dbPath')
        self.token = os.environ.get('token_oop')
        dbBase = os.environ.get('dbBase')

        self.dbClient =  Client(dbLogin, dbPassword, dbPath, dbBase)




        #print(self.client)

    def isCommand(self, txt):
        isCommand = False
        name = None
        txt1 = txt.split()
        if(txt1[0][0] == '/'):
            isCommand = True
            name = txt1[0][1:]
        return isCommand, name

    def log(self, data, dataType = ''):
        print(data)

        if dataType == 'w':
            logging.warning(data)
        elif dataType == 'e':
            logging.error(data)
        else:
            logging.info(data)

    @staticmethod
    def getDataFolder():
        return "bot_data"

    @staticmethod
    def extractJson(str='{}'):
        try:
            h = json.JSONDecoder().decode(str)
        except Error:
            h = {}
        return h

class Client:
    client = None
    data = None
    def __init__(self, dbLogin, dbPassword, dbPath, dbBase):
        self.client =  MongoClient(f'mongodb+srv://{dbLogin}:{dbPassword}@{dbPath}')
        self.data = self.client[dbBase]

        #self.insertCommands()
        #self.insertResults()

    def insertData(self, dataset, collection):
        coll = self.data[collection]
        batch_size = 1000
        inserts = []
        count = 0

        for line in dataset:
            inserts.append(InsertOne(line))

            count += 1

            if count == batch_size:
                coll.bulk_write(inserts)
                inserts = []
                count = 0
        if inserts:
            coll.bulk_write(inserts)
            count = 0

    def insertCommands(self):
        commands = [
            {'name': 'help', 'descr' : 'This command shows help.'},
            {'name' : 'answer', 'descr': 'This command creates an answer. The bot will ask - ', 'args': [
                {'code': 'NAME', 'name': 'Имя слушателя', 'paramtype': 'string'},
                {'code': 'BLOCK', 'name': 'Название блока', 'paramtype': 'string'},
                {'code': 'SUCCESS', 'name': 'Решение принято? Y = Да, N = Нет', 'paramtype': 'boolean'},
                {'code': 'ASKED', 'name': 'У студента есть доп вопросы? Y = Да, N = Нет', 'paramtype': 'boolean'},
                ]
            }
        ]
        self.insertData(commands, 'commands')

    def insertResults(self):
        dictionary = [
            {'name' : 'greet', 'replies' :  ['#NAME#, здравствуйте!', '#NAME#, добрый день!', '#NAME#, доброго дня!']} ,
            {'name' : 'thank', 'replies' :   ['Спасибо за выполненное домашнее задание к блоку *#BLOCK#*!',
                      'Благодарю, что выполнили домашнее задание к блоку *#BLOCK#*!',
                      'Здорово, что Вы сделали домашнее задание к блоку *#BLOCK#*!',
                      'Здорово, что Вы выполнили домашнее задание к блоку *#BLOCK#*!',
                      'Благодарим за выполнение домашнего задания к блоку *#BLOCK#*!',
                      'Благодарю за выполненную работу к блоку *#BLOCK#*!'
                      ]},
            {'name' : 'success', 'replies' :   ['Вы удачно реализовали …',
                        'Отмечу, что получилось …',
                        'Вам отлично удалось выполнить…',
                        'У Вас отлично получилось ...',
                        'Вам удалось ...',
                        'Здорово, что вы посмотрели на проблему так-то…  и это позволило…'

                        ]},
            {'name' : 'improve', 'replies' :   ['Хочу обратить ваше внимание на …',
                        'Обратите внимание, что …',
                        'Как специалист хочу предостеречь вас  от …',
                        'Будьте внимательны - …',
                        'Примите, пожалуйста, во внимание, что …',
                        'В дальнейшем вы можете…',
                        'Также советую обратить внимание на…'
                        ]},
            {'name' : 'asks', 'replies' :   [
                'Отвечаю на Ваш вопрос - ...',
                'Ответ на Ваш вопрос - ',
                'Позвольте ответить на вопрос - ',
                'Вопрос интересный, вот ответ - '
            ]},
            {'name' : 'result_good', 'replies' :   [
                'Желаю удачи в воплощении вашего проекта!',
                'Удачи в дальнейшем обучении!',
                'Продолжайте в том же духе!',
                'Зачет!',
                'Вы проделали отличную работу!'
            ]},
           {'name' : 'result_neg', 'replies' :   [
                'Пожалуйста, внесите исправления в решение.',
                'Исправьте, пожалуйста, замечания, указанные выше.',
                'Пожалуйста, выполните исправления.',
                'Пожалуйста, доработайте свое решение.',
                'Пока работа требует доработки. ',
                'Внесите, пожалуйста, правки.'
            ]}

            ]
        self.insertData(dictionary, 'dictionary')


class Bot:
    bot  = None
    commands = {}
    def __init__(self, token):
        bot = telebot.TeleBot(token)
        self.bot = bot

        commands = self.getCommands()
        arr = []
        for i in range(0, len(commands)):

            command = commands[i]
            cmd = command['name']

            descr = '' if 'descr' not in command else command['descr']
            args = [] if 'args' not in command else command['args']

            #print(descr, args)


            command1 = None

            if(cmd == 'help'):
                command1 = CommandHelp(cmd, descr, args)
            elif cmd == 'answer':
                command1 = CommandAnswer(cmd, descr, args)
            else:
                command1 = Command(cmd, descr, args)

            self.commands[cmd] = command1
            arr.append(telebot.types.BotCommand(f'/{command1.name}', command1.descr))

        self.bot.set_my_commands(arr)

    def getCommands(self):
        commands = [
            {'name': 'help', 'descr' : 'This command shows help.'},
            {'name' : 'answer', 'descr': 'This command creates an answer. The bot will ask - ', 'args': [
                {'code': 'NAME', 'name': 'Имя слушателя', 'paramtype': 'string'},
                {'code': 'BLOCK', 'name': 'Название блока', 'paramtype': 'string'},
                {'code': 'SUCCESS', 'name': 'Решение принято? Y = Да, N = Нет', 'paramtype': 'boolean'},
                {'code': 'ASKED', 'name': 'У студента есть доп вопросы? Y = Да, N = Нет', 'paramtype': 'boolean'},
                ]
            }
        ]
        #commandsStr = json.JSONEncoder().encode(commands)

        #print( commandsStr)

        #commands = os.environ.get('commands')
        return commands

    def getCommandByName(self, cmd):
        if cmd in self.commands:
            return self.commands[cmd]
        return None

    def getResult(self):
        pass


    def execDefault(self, message):
        # bot.send_message(message.chat.id, message.text)
        # print(message)
        msg = ''
        if (len(msg) > 0):
            self.bot.send_message(message.chat.id, msg)

    def getAnswer(self, message, isCommand = False):
        hist = History(message.from_user.id, message.text, isCommand)
        if hist.askCommand:
            return 'Insert command', None

        answer, markup = self.analyzeHistory(hist, message.text)
        return answer, markup


    def analyzeHistory(self, hist, txt):
        markup = None
        lastCode = ''

        command = self.commands['answer']
        k = 0
        for i in range(0, len(command.params)):
            code = command.params[i].code
            if (code not in hist.history):
                hist.history[code] = None
                ans = 'Введите *' + command.params[i].name + '*'
                lastCode = code
                break
            else:
                if hist.history[code] == None:
                    if not hist.isCommand:
                        k += 1
                        hist.history[code] = txt
                    else:
                        ans = 'Введите *' + command.params[i].name + '*'
                        lastCode = code
                        break
                else:
                    k += 1

        if (k == len(command.params)):
            # генерим
            ans = resultObj.getResult(hist)

        else:
            print(k)
            print(hist.history)
            f = open(hist.path, 'w+')
            f.write(json.JSONEncoder().encode(hist.history))
            f.close()

        if (len(ans) == 0):
            ans = 'I dont\'t understand you'

        if lastCode == 'SUCCESS':
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtn1 = types.KeyboardButton('Y')
            itembtn2 = types.KeyboardButton('N')
            markup.add(itembtn1, itembtn2)
        else:
            markup = None

        return ans, markup



class Command:
    name = ''
    descr = ''
    params = []
    def __init__(self, name, descr, params):
        self.name = name
        self.descr = descr
        params1 = []
        for param in params:
            params1.append(Parameter(param))
        self.params = params1


class CommandHelp(Command):
    def exec(self, message):

        help = ''
        for cmd in botObj.commands:
            command = botObj.commands[cmd]
            # print(command)

            if (command.descr):
                descr = command.descr
                help = help + "/" + cmd + ' - ' + descr + '\n'
            else:
                help = help + "/" + cmd + '\n'

            if ( command.params):
                args = command.params
                if (args is not None):
                    for i in range(0, len(args)):
                        help += args[i].name + ': ' + args[i].paramtype + '\n'

        return help, None



class CommandAnswer(Command):
    def exec(self, message):
        answer, markup = botObj.getAnswer(message, True)

        return answer, markup
        #botObj.bot.send_message(message.chat.id, message.text)

class Parameter:
    name = ''
    code = ''
    paramtype =''
    def __init__(self, param):
        self.name = '' if 'name' not in param else param['name']
        self.code =  '' if 'code' not in param else param['code']
        self.paramtype =  '' if 'paramtype' not in param else param['paramtype']


class History:
    userId = None
    txt = ''
    isCommand = False
    path = ''
    historyStr = ''
    history = {}
    askCommand = False

    def __init__(self, userId, txt, isCommand = False):
        self.userId = userId
        self.txt = txt
        self.isCommand = True if isCommand else False
        self.getHistory()

    def getHistory(self):
        txt = self.txt
        markup = None

        ans = ''
        lastCode = ''
        isCommand = self.isCommand

        self.getHistoryPath()
        self.getHistoryStr()



        # os.remove(path)

        if (len(self.historyStr) == 0):
            history = Env.extractJson()
        else:
            history = Env.extractJson(self.historyStr)
        print('history', history)

        self.history = history

    def getHistoryStr(self):
        historyStr = ''
        try:
            f = open(self.path, 'r')
            historyStr = f.read()
            f.close()
        except FileNotFoundError:
            if (self.isCommand == False):
                self.askCommand = True

        print('historyStr', historyStr)
        self.historyStr =   historyStr

    def getHistoryPath(self):
        data_folder = Env.getDataFolder()
        user_folder = data_folder + f'/{self.userId}'
        if not os.path.isdir(user_folder):
            os.makedirs(user_folder)
        path = user_folder + '/history.json'
        print('path', path)
        self.path =  path

class Result:
    parts = {}
    def __init__(self):
        dictionary = self.getDictionary()
        for i in range(0, len(dictionary)):
            d = dictionary[i]
            key = d['name']
            self.parts[key] = ResultPart(key, d['replies'])

    def getResult(self, hist):

        success = hist.history['SUCCESS'] == 'Y'
        asked = hist.history['ASKED'] == 'Y'
        ans = ''

        for key in self.parts:
            # print(key)
            part = self.parts[key].getRand()

            if (success and key == 'result_neg' or not success and key == 'result_good'):
                continue
            if (not asked and key == 'asks'):
                continue

            for i in hist.history:
                repl = ''
                if (hist.history[i] is not None):
                    repl = hist.history[i]
                part = part.replace(f'#{i}#', repl)

            ans += part + '\n\n'

        os.remove(hist.path)
        return ans

    def getDictionary(self):
        dictionary = [
            {'name' : 'greet', 'replies' :  ['#NAME#, здравствуйте!', '#NAME#, добрый день!', '#NAME#, доброго дня!']} ,
            {'name' : 'thank', 'replies' :   ['Спасибо за выполненное домашнее задание к блоку *#BLOCK#*!',
                      'Благодарю, что выполнили домашнее задание к блоку *#BLOCK#*!',
                      'Здорово, что Вы сделали домашнее задание к блоку *#BLOCK#*!',
                      'Здорово, что Вы выполнили домашнее задание к блоку *#BLOCK#*!',
                      'Благодарим за выполнение домашнего задания к блоку *#BLOCK#*!',
                      'Благодарю за выполненную работу к блоку *#BLOCK#*!'
                      ]},
            {'name' : 'success', 'replies' :   ['Вы удачно реализовали …',
                        'Отмечу, что получилось …',
                        'Вам отлично удалось выполнить…',
                        'У Вас отлично получилось ...',
                        'Вам удалось ...',
                        'Здорово, что вы посмотрели на проблему так-то…  и это позволило…'

                        ]},
            {'name' : 'improve', 'replies' :   ['Хочу обратить ваше внимание на …',
                        'Обратите внимание, что …',
                        'Как специалист хочу предостеречь вас  от …',
                        'Будьте внимательны - …',
                        'Примите, пожалуйста, во внимание, что …',
                        'В дальнейшем вы можете…',
                        'Также советую обратить внимание на…'
                        ]},
            {'name' : 'asks', 'replies' :   [
                'Отвечаю на Ваш вопрос - ...',
                'Ответ на Ваш вопрос - ',
                'Позвольте ответить на вопрос - ',
                'Вопрос интересный, вот ответ - '
            ]},
            {'name' : 'result_good', 'replies' :   [
                'Желаю удачи в воплощении вашего проекта!',
                'Удачи в дальнейшем обучении!',
                'Продолжайте в том же духе!',
                'Зачет!',
                'Вы проделали отличную работу!'
            ]},
           {'name' : 'result_neg', 'replies' :   [
                'Пожалуйста, внесите исправления в решение.',
                'Исправьте, пожалуйста, замечания, указанные выше.',
                'Пожалуйста, выполните исправления.',
                'Пожалуйста, доработайте свое решение.',
                'Пока работа требует доработки. ',
                'Внесите, пожалуйста, правки.'
            ]}

            ]


        return dictionary

class ResultPart:
    key = ''
    vars = []
    def __init__(self, key, vars = []):
        self.key = key
        self.vars = vars

    def getRand(self):
        return choice(self.vars)


envObj = Env()
botObj = Bot(envObj.token)
resultObj = Result()

bot = botObj.bot




@bot.message_handler()
def other(message):
    # bot.send_message(message.chat.id, message.text)
    #envObj.log(bot)
    #envObj.log(message)

    isCommand, name = envObj.isCommand(message.text)
    #envObj.log(isCommand)
    #envObj.log(name)

    markup = None

    if isCommand:
        command = botObj.getCommandByName(name)
        #print(command)
        answer, markup = command.exec(message)
    else:
        answer, markup = botObj.getAnswer(message)


    msg = answer
    if (len(msg) > 0):
        botObj.bot.reply_to(message, msg, parse_mode='Markdown', reply_markup=markup)


bot.polling(none_stop=True)
