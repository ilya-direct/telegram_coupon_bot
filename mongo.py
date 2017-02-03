#! /usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import re

connection = MongoClient('mongodb://localhost:27017/')

#
db = connection.promo
#

#
db.drop_collection('coupons')

# ваолд
# Burger King
db.coupons.insert({
    'name': 'BurgerKing',
    'code': '9894',
    'description': '2 Вопер обеда(2 Воппера, 2 фри мал, 2 напитка) за 399'
})
db.coupons.insert({
    'name': 'BurgerKing',
    'code': '9903',
    'description': 'Луковые колечки  за 69'
})
db.coupons.insert({
    'name': 'BurgerKing',
    'code': '9869',
    'description': 'Чизбургер бесплатно при покупке Сырного Джо(за 199)'
})

db.coupons.insert({
    'name': 'BurgerKing',
    'code': '9277',
    'description': '2 кинг фри(мал) за 99'
})

# KFC
db.coupons.insert({
    'name': 'KFC',
    'code': '3067',
    'description': 'Боксмастер, станд. фри за 171(вместо 231)'
})
db.coupons.insert({
    'name': 'KFC',
    'code': '3066',
    'description': 'Сандерс, напиток(0,4), фри(мал) за 139 (вместо 186)'
})
db.coupons.insert({
    'name': 'KFC',
    'code': '3069',
    'description': 'Биггер, фри(станд) за 191 вместо(251)'
})

db.coupons.insert({
    'name': 'KFC',
    'code': '3070',
    'description': 'Снекбокс(стрипсы), напиток(0,4) за 119 (вместо 153)'
})

#uber
db.coupons.insert({
    'name': 'uber',
    'code': 'MCzima17',
    'description': 'по карте  Mastercard скидка 50% на первые пять поездок(до 19.02.2017)'
})

# СпецКупоны
db.coupons.insert({
    'name': 'BurgerKing',
    'number': '1',
    'description': '2 Биг Кинг по цене одного',
    'price': 25,
    'special': bool(1),
})
db.coupons.insert({
    'name': 'BurgerKing',
    'number': '2',
    'description': 'Воппер, 2 кинг фри(мал), лук. кольца, 3 соуса ЗА ПОЛЦЕНЫ',
    'price': 25,
    'special': bool(1),
})

# db.coupons.save({'name': 'user 2', 'level': 2})
# db.coupons.insert({'name': 'user 3', 'level': 3})

#
print db.coupons.full_name

#
for user in db.coupons.find():
    print user

#
coupons = db.coupons.find({}, {'login': 1, 'name': 1})

#
user = db.coupons.find_one({'name': 'user 1'})

#
# print user['level']
# user['level'] = 7

#
# db.coupons.save(user)

#
# db.coupons.remove(user)

#
# db.coupons.update({'name': 'user 2'}, {"$set": {'level': 5}})

#
print 'Count', db.coupons.count()
print 'Count lvl=2', db.coupons.find({'level': 2}).count()

#
for user in db.coupons.find().sort('level'):
    print user
    db.coupons.find({}).sort([('status', 1), ('level', -1)])

for user in db.coupons.find().skip(1).limit(2):
    print user

#
for user in db.coupons.find().where('this.name == "user 2" || this.level>3'):
    print user

#
for user in db.coupons.distinct('level'):
    print user

#

regex = re.compile('us', re.I | re.U)
result = db.collection.find({'name': regex}).count()
print result
