# -*- coding: utf-8 -*-
import telebot
import logging
import time
from telebot import types
from pymongo import MongoClient
import re

connection = MongoClient('mongodb://localhost:27017/')
db = connection.promo

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)  # Outputs debug messages to console.

bot = telebot.TeleBot("328517248:AAFAtzi8wE1QwruPrtz1pp6KVBA1Eyqqjnw")

menu_markup = types.ReplyKeyboardMarkup(row_width=3)
itembtn1 = types.KeyboardButton(u'Burger King \U0001F451')
itembtn2 = types.KeyboardButton(u'KFC \U0001F425')
itembtn3 = types.KeyboardButton(u'Uber \U0001F693')
itembtn4 = types.KeyboardButton(u'Спец Купоны ' + u'\U0001F525')
itembtn5 = types.KeyboardButton(u'Добавь купон')
itembtn6 = types.KeyboardButton(u'Поддержка')
menu_markup.row(itembtn1, itembtn2)
menu_markup.row(itembtn3, itembtn4)
menu_markup.row(itembtn5, itembtn6)

default_markup = types.ReplyKeyboardRemove(selective=False)

couponConditions = {
    u'Burger King \U0001F451': {"name": "BurgerKing", "special": {"$ne": bool(1)}},
    u'KFC \U0001F425': {"name": "KFC", "special": {"$ne": bool(1)}},
    u'Uber \U0001F693': {"name": "uber", "special": {"$ne": bool(1)}},
    # 'Special': {"special": bool(1)}
}


# /start
@bot.message_handler(commands=['start'])
def handle_start_help(message):
    bot.send_message(message.chat.id, "Выберете из списка: ", reply_markup=menu_markup)
    # bot.pre_message_subscribers_next_step[message.from_user.id] = []
    # bot.message_subscribers_next_step[message.from_user.id] = []
    bot.pre_message_subscribers_next_step.pop(message.from_user.id, None)
    bot.register_next_step_handler(message, handle_vendor)
    return


def handle_vendor(message):
    if message.text == '/start':
        return
    msg = ''
    if message.text == u'Поддержка':
        handle_support(message)
        return

    if message.text == u'Добавь купон':
        handle_new_coupon(message)
        return

    if message.text == (u'Спец Купоны ' + u'\U0001F525'):
        special_coupons = db.coupons.find({"special": bool(1)})
        for coupon in special_coupons:
            msg = msg + '#' + coupon['number'] + ' - ' + coupon['name'] + ' - ' + coupon['description'] + '\n'
        bot.send_message(message.chat.id, msg)
        bot.send_message(message.chat.id,
                         'Специальные купоны стоят 20 рублей! Оплата Qiwi на номер +79636568377. '
                         'После оплаты введите команду в формате: #<номер купона> <4 последние цифры кода операции>. \n'
                         'Пример #2 4959. \n'
                         'Для выхода введите "!"'
                         , reply_markup=default_markup)
        bot.register_next_step_handler(message, proceed_payment)
        return
    cond = couponConditions.get(message.text, bool(0))
    if cond:
        for coupon in db.coupons.find(cond):
            msg = msg + '<b>' + coupon['code'] + '</b>' + ' - ' + coupon['description'] + '\n'

    bot.send_message(message.chat.id, msg if msg else 'Неверная команда.  Попробуйте снова',
                     parse_mode='HTML')
    bot.register_next_step_handler(message, handle_vendor)
    return


# start end

# /support
# @bot.message_handler(commands=['support'])
def handle_support(message):
    if message.text == '/start':
        return
    bot.send_message(message.from_user.id, u'Напишите сообщение в поддержку. Для выхода отправьте "!"',
                     reply_markup=default_markup)
    bot.register_next_step_handler(message, support)


def support(message):
    if message.text == '/start':
        return
    if message.text == '!':
        bot.send_message(message.from_user.id, u'Отменена отправка сообщения', reply_markup=menu_markup)
    else:
        bot.send_message(169605017, u'Поддержка от: ' + str(message.from_user.id) + '\n ' + message.text)
        bot.send_message(message.from_user.id,
                         u'Ваше сообщение успешно отправлено в поддержку, ожидайте ответа. Спасибо!',
                         reply_markup=menu_markup)
    bot.register_next_step_handler(message, handle_vendor)
    return


# support end

# /add ----
# @bot.message_handler(commands=['add'])
def handle_new_coupon(message):
    if message.text == '/start':
        return
    bot.send_message(message.from_user.id, u'Введите новый промо в произвольном формате.'
                                           u'Для выхода отправьте: "!"', reply_markup=default_markup)
    bot.register_next_step_handler(message, new_coupon)


def new_coupon(message):
    if message.text == '/start':
        return
    if message.text == '!':
        bot.send_message(message.from_user.id, u'Отменена отправка купона', reply_markup=menu_markup)
    else:
        bot.send_message(169605017, u'Купон от: ' + str(message.from_user.id) + '\n ' + message.text)
        bot.send_message(message.from_user.id, u'Спасибо за помощь в развитии! Купон проходит модерацию. '
                                               u'После добавления мы обязательно сообщим Вам!',
                         reply_markup=menu_markup)
    bot.register_next_step_handler(message, handle_vendor)
    return


# add end

# for admin
@bot.message_handler(commands=['send'])
def send_message_to_client(message):
    if message.from_user.id == 169605017:
        text = message.text.split(' ', 2)
        try:
            bot.send_message(text[1], text[2])
            bot.send_message(message.from_user.id, u'Письмо отправлено')
        except Exception as e:
            logger.error(e.message)
            bot.send_message(message.from_user.id, u'Ошибка при отправки письма')

        return


# for admin end

# Payment
# @bot.message_handler(content_types=['text'], regexp='^#\d{1,3} \d{4}$')
# def handle_payment(message):
#    bot.send_message(message.chat.id, 'Ожидайте проверки оплаты(до 2-х часов)')
#    bot.send_message(169605017, u'Проверьте оплату от ' + str(message.from_user.id) + u' текст : ' + message.text)
#    pass


def proceed_payment(message):
    if message.text == '/start':
        return
    if message.text == '!':
        bot.send_message(message.from_user.id, u'Отмена. Выберете другой пункт:', reply_markup=menu_markup)
        bot.register_next_step_handler(message, handle_vendor)
        return
    pattern = re.compile("^#\d{1,3} \d{4}$")
    if pattern.match(message.text):
        bot.send_message(message.chat.id, 'Ожидайте проверки оплаты(до 2-х часов)')
        bot.send_message(169605017, u'Проверьте оплату от ' + str(message.from_user.id) + u' текст : ' + message.text,
                         reply_markup=menu_markup)
        bot.register_next_step_handler(message, handle_vendor)
    else:
        bot.send_message(message.chat.id, 'Неверный формат. Пример: "#43 3423". Для выхода отправьте "!"')
        bot.register_next_step_handler(message, proceed_payment)
    return


while 1:
    try:
        time.sleep(5)
        bot.polling()
    except Exception as e:
        logger.error(e.message)
