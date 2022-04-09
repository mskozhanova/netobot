import telebot
import re
from random import choice

import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
#print(dotenv_path)

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

token =   os.environ.get('token')

bot = telebot.TeleBot(token)

dictionary = {
    'greet': ['#NAME#, здравствуйте!', '#NAME#, добрый день!', '#NAME#, доброго дня!'],
    'thank': ['Спасибо за выполненное домашнее задание к блоку #BLOCK#!', 'Благодарю, что выполнили домашнее задание к блоку #BLOCK#!',
        'Здорово, что Вы сделали домашнее задание к блоку #BLOCK#!',
        'Здорово, что Вы выполнили домашнее задание к блоку #BLOCK#!',
        'Благодарим за выполнение домашнего задания к блоку #BLOCK#!',
        'Благодарю за выполненную работу к блоку #BLOCK#!'
    ],
    'success': ['Вы удачно реализовали …',
        'Отмечу, что получилось …',
        'Вам удалось чётко сформулировать…',
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
        {'code': 'SUCCESS', 'name': 'Решение принято?', 'type': 'Y/N'},
        ],
        'example': '/answer [Петр] [Базовые функции PHP] [Y]'
    }
}


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

        if('example' in command):
            help += 'Example: ' + command['example'] + '\n'

    bot.send_message(message.chat.id, help)

@bot.message_handler(commands=['answer'])
def help(message):

    tmp = message.text.strip()[1:]
    #print(tmp)

    tmp1 = tmp.split(maxsplit=1)
    #print(tmp1)

    ans = '';
    args = []
    if(len(tmp1) > 1):
        args = []
        args = re.findall(r'\[.+?\]', tmp1[1])
        #print(args)
        args = list(map(lambda x: x[1:len(x)-1], args))
        print(args)
        #ans = ' '.join(args)

        if(len(args) == 0):
            ans = 'Input name, block and success'
        else:
            name = args[0]
            block = '...'
            success = False
            if(len(args) > 1):
                block = args[1]
            if(len(args) > 2):
                success = args[2] == 'Y'

            print(success)

            for key in dictionary:
                #print(key)
                part = choice(dictionary[key])

                if(success and key == 'result_neg' or not success and key == 'result_good'):
                    continue;

                ans += part.replace('#NAME#', name).replace('#BLOCK#', '"' + block + '"') + '\n\n'
    else:
        ans = 'no arguments'


    bot.send_message(message.chat.id, ans)


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

@bot.message_handler()
def help(message):
    help = 'I don\'t understand you!';
    bot.send_message(message.chat.id, help)


bot.polling(none_stop=True)
