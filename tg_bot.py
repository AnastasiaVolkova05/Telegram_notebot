import asyncio
import logging
import json
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

import config # this file should contain your bot token in a variable BOT_TOKEN
import frases

try:
    with open("database.json", "x" , encoding='utf-8') as f:
        pass
    with open("database.json", "w" , encoding='utf-8') as f:
        db = {}
        json.dump(db, f)

except:
    with open("database.json", "r" , encoding='utf-8') as f:
        db = json.load(f)
        dp = Dispatcher(storage=MemoryStorage())
        users_add = []
        users_del = []
        users_edit = []



        def add_note(note, user):
            user = str(user)
            with open("database.json", "w", encoding='utf-8') as f:   
                print(db.keys())
                print(user)
                if user not in db.keys():
                    db.update({user : [note]})
                    print(db)
                    json.dump(db, f)
                    return "Succes"
                else:
                    db.get(user).append(note)
                    json.dump(db, f)
                    return "Yeah"
                
        def edit(note, user, ind):
            user = str(user)
            with open("database.json", "w", encoding='utf-8') as f:   
                print(db.keys())
                print(user)
                if user not in db.keys():
                    return "Нет заметок"
                else:
                    db.get(user)[ind - 1] = note
                    json.dump(db, f)
                    return "Edited"



        def delete_note(number, user):
            user = str(user)
            if db.get(user) == None or len(db.get(user)) < number:
                return "You do something wrong"
            else:
                with open("database.json", "w", encoding='utf-8') as f:
                    del db.get(user)[number - 1]
                    json.dump(db, f)
                return "Okey"
        

            
        @dp.message(Command('help'))
        async def help_handler(msg: Message):
            await msg.answer(frases.help_frase)


        @dp.message(Command('start'))
        async def start_handler(msg: Message):
            await msg.answer(f"Привет {(msg.from_user.full_name)}! Это бот - заметки. Чтобы узнать подробнее нажми  /help")


        @dp.message(Command('add_note'))
        async def add_hendler(msg: Message):
            if msg.from_user.id in users_del:
                users_del.remove(msg.from_user.id)
            if msg.from_user.id in users_edit:
                users_edit.remove(msg.from_user.id)
            if msg.from_user.id not in users_add:
                users_add.append(msg.from_user.id)
                await msg.answer("Теперь вводите заметки по одной.")
            else:
                await msg.answer("Вы уже добавляете заметки")

        @dp.message(Command('delete_note'))
        async def delete_hendler(msg: Message):
            if msg.from_user.id in users_add:
                users_add.remove(msg.from_user.id)
            if msg.from_user.id in users_edit:
                users_edit.remove(msg.from_user.id)
            print(db.get(str(msg.from_user.id)))
            if db.get(str(msg.from_user.id)) != None:
                for i in range(len(db.get(str(msg.from_user.id)))):
                    await msg.answer(str(i + 1) + '. ' + db.get(str(msg.from_user.id))[i])
                users_del.append(msg.from_user.id)
                await msg.answer("Вводите номера заметок, которые хотите удалить, по очереди(разными сообщениямиб 1 сообщение - 1 номер).")
            else:
                await msg.answer("Заметок нет")

            
        @dp.message(Command('view_note'))
        async def view_handler(msg: Message):
            if msg.from_user.id in users_add:
                users_add.remove(msg.from_user.id)
            elif msg.from_user.id in users_del:
                users_del.remove(msg.from_user.id)
            elif msg.from_user.id in users_edit:
                users_edit.remove(msg.from_user.id)
            if db.get(str(msg.from_user.id)) != None:
                for i in range(len(db.get(str(msg.from_user.id)))):
                    await msg.answer(str(i + 1) + '. ' + (db.get(str(msg.from_user.id)))[i])
            else:
                await msg.answer("Заметок нет")

        @dp.message(Command('edit'))
        async def view_handler(msg: Message):
            if msg.from_user.id in users_add:
                users_add.remove(msg.from_user.id)
            elif msg.from_user.id in users_del:
                users_del.remove(msg.from_user.id)
            print(db.get(str(msg.from_user.id)))
            if db.get(str(msg.from_user.id)) != None:
                for i in range(len(db.get(str(msg.from_user.id)))):
                    await msg.answer(str(i + 1) + '. ' + db.get(str(msg.from_user.id))[i])
                users_edit.append(msg.from_user.id)
                await msg.answer(frases.edit_frase)
            else:
                await msg.answer("Заметок нет")


        @dp.message()
        async def message_handler(msg: Message):
            if msg.from_user.id in users_add:
                app = msg.text + '; дата заметки: ' + str(msg.date)[0:10]
                await msg.answer(add_note(app, msg.from_user.id))
            elif msg.from_user.id in users_del:
                indexes = []
                for i in range(1 , len(db.get(str(msg.from_user.id))) + 1):
                    indexes.append(str(i))
                if msg.text in indexes:
                    await msg.answer(delete_note(int(msg.text), msg.from_user.id))
                else:
                    await msg.answer("Error")
            elif msg.from_user.id in users_edit:
                text = msg.text.strip()
                ind = int(text[0])
                if ind > len(db.get(str(msg.from_user.id))) or ind < 1:
                    users_edit.remove(msg.from_user.id)
                    await msg.answer("Заметки с таким номером еще не существует")
                else:
                    users_edit.remove(msg.from_user.id)
                    await msg.answer(edit(text[2:] + '; заметка переделана: ' + str(msg.date)[0:10],msg.from_user.id, ind))
            else:
                await msg.answer("Предлагаю снова почитать /help")


        async def main():
            bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
            await dp.start_polling(bot)


        if __name__ == "__main__":
            logging.basicConfig(level=logging.INFO)
            asyncio.run(main())
