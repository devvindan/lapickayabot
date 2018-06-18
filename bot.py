from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import BaseFilter
import re
import json
import random
import logging
import string
import os


class LapickayaBot:

    def __init__(self):

        # Load bot answers and other info

        with open('data.json', 'r') as f:
            bot_data = json.load(f)

        self.users = { "id": { "questions": [], "last": "?" } }

        self.token = str(os.getenv('TOKEN'))
        self.app_port = int(os.getenv('PORT', '8443'))

        self.replies = bot_data["replies"]
        self.definitions = bot_data["definitions"]

        # Creating bot core

        self.updater = Updater(token=self.token)
        self.dispatcher = self.updater.dispatcher

        #Making handlers

        start_handler = CommandHandler('start', self.start)
        help_handler = CommandHandler('help', self.help)
        list_handler = CommandHandler('list', self.list)
        listdef_handler = CommandHandler('listdef', self.listdef)
        lookup_handler = CommandHandler('lookup', self.lookup, pass_args=True)
        challenge_handler = CommandHandler('challenge', self.challenge)

        default_message_handler = MessageHandler(Filters.all, self.message_handler)

        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(help_handler)
        self.dispatcher.add_handler(list_handler)
        self.dispatcher.add_handler(listdef_handler)
        self.dispatcher.add_handler(lookup_handler)
        self.dispatcher.add_handler(challenge_handler)
        self.dispatcher.add_handler(default_message_handler)



    def start(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text=self.replies["start"])

    def help(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text=self.replies["help"])

    def listdef(self, bot, update):
        lst = list(dict(self.definitions).keys())
        lst.sort()
        defs = [self.definitions[key] for key in lst]
        result = "\n".join(
            ["{}. {}\n\n{}\n".format(index + 1, lst[index], defs[index]) for index in range(len(lst))])
        bot.send_message(chat_id=update.message.chat_id, text=result)

    def list(self, bot, update):
        lst = list(dict(self.definitions).keys())
        lst.sort()
        result = "\n".join(
            ["{}. {}".format(index + 1, lst[index]) for index in range(len(lst))])
        bot.send_message(chat_id=update.message.chat_id, text=result)

    def challenge(self, bot, update):
        user_id = update.message.chat_id
        bot.send_message(chat_id=user_id, text=self.replies["challenge"])
        lst = list(dict(self.definitions).keys())
        first = random.choice(lst)
        lst.remove(first)
        self.users[user_id] = { "last": first, "questions": lst }
        bot.send_message(chat_id=user_id, text="Первый вопрос: {}".format(first))

    def lookup(self, bot, update, args):
        if len(args) == 0:
            bot.send_message(chat_id=update.message.chat_id, text="Нужно указать название определения!")
        definition = " ".join(args).lower()
        dict_lower = {k.lower(): v for k, v in self.definitions.items()}
        if definition in dict_lower:
            bot.send_message(chat_id=update.message.chat_id, text="{}: {}".format(definition,dict_lower[definition]))
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Определение не найдено!")

    def message_handler(self, bot, update):
        user_id = update.message.chat_id
        if user_id in self.users:
            last = self.users[user_id]["last"]
            if self.definitions[last].lower() == update.message.text.lower():
                bot.send_message(chat_id=user_id, text="Правильно!")
            else:
                bot.send_message(chat_id=user_id, text=
                                 "Неправильно!\n{} - {}".format(last, self.definitions[last]))
            if len(self.users[user_id]["questions"]) == 0:
                del self.users[user_id]
                return
            new = random.choice(self.users[user_id]["questions"])
            self.users[user_id]["last"] = new
            self.users[user_id]["questions"].remove(new)
            bot.send_message(chat_id=user_id, text=
            "Вопросов осталось: {}\n{}?".format(len(self.users[user_id]["questions"]) + 1, new))
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Не понимаю вас... Попробуйте /help")



logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

bot = LapickayaBot()
#bot.updater.start_polling()


bot.updater.start_webhook(listen="0.0.0.0",
                      port=bot.app_port,
                      url_path=bot.token)
bot.updater.bot.set_webhook("https://lapickayabot.herokuapp.com/" + bot.token)
bot.updater.idle()

