import asyncio
import logging
import sys, re
from os import getenv
import config
from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,  ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.methods.delete_message import DeleteMessage



# ------------------  Redis storage ---------------------
# from aiogram.fsm.storage.redis import RedisStorage

# storage = RedisStorage(
#     host=REDIS_HOST, 
#     port=REDIS_PORT,
#     db=REDIS_DB,
#     password=REDIS_PASSWORD,
#     # и т.д.
# )

# dp = Dispatcher(bot, storage=storage)
# -------------------------------------------------------

# ------------------- Postgres storage ---------------------
# from AiogramStorages.storages import PGStorage

# storage = PGStorage(username='postgres', password='YourPassword', db_name='YourDbName')  
# dp = Dispatcher(bot, storage=storage)
# ------------------------------------------------------------



# Bot token can be obtained via https://t.me/BotFather
#TOKEN = config.TELEGRAM_BOT_TOKEN
TOKEN = getenv("BOT_TOKEN")
 

# All handlers should be attached to the Router (or Dispatcher)
form_router = Router()
dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
messages_del = []
LANG_EN_BUT = "🇬🇧 English"
LANG_UZ_BUT = "🇺🇿 Uzbek"
LANG_RU_BUT = "🇷🇺 Russian"


class ClientState(StatesGroup):
    LANG_SELECTION = State()
    START_MESS = State()
    MAIN_MENU = State()
    MAIN_MENU_LOCATION = State()
    PERS_CAB_AUTH = State()
 
 

async def  Translate_Message(MessageName: str, state: FSMContext) -> any:
    data =  await state.get_data() 
    lang = data["LANG_SELECTION"]  

    if lang == LANG_EN_BUT:
       return config.LANG_EN[MessageName]
        
    if lang == LANG_UZ_BUT:
       return config.LANG_UZ[MessageName]
    
    if lang == LANG_RU_BUT:
       return config.LANG_RU[MessageName]
    


async def RemoveMessages():
    for i in messages_del:
      try:
          await bot.delete_message(chat_id=i[0],message_id=i[1])
      except:
          logging.error("Unable to delete message: "  + str(i[0]) + " - " + str(i[1]) )
          pass 

    messages_del.clear()

async def AddMessToRemove(message: Message = None):
    if message != None:
      messages_del.append([message.chat.id, message.message_id])
 
@form_router.message(CommandStart())
async def command_start_handler(message: Message, state = FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
 
    logging.info("The user with name '" + message.from_user.full_name + "' has started the bot.")

    msg = \
    config.LANG_RU["Hello"]+f"{html.bold(message.from_user.full_name)}! " + config.LANG_RU["Hello_mess"] + '\n\n' + \
    config.LANG_EN["Hello"]+f"{html.bold(message.from_user.full_name)}! " + config.LANG_EN["Hello_mess"] + '\n\n' + \
    config.LANG_UZ["Hello"]+f"{html.bold(message.from_user.full_name)}! " + config.LANG_UZ["Hello_mess"] 
 
    
    await state.set_state(ClientState.START_MESS) 
    await message.answer(msg)
    await lang_sel_handler(message, state)  
   
     


 
@form_router.message(ClientState.START_MESS)
async def lang_sel_handler(message: Message, state: FSMContext) -> None:
        
        kb = [
        
        [KeyboardButton(text=LANG_UZ_BUT)],
        [KeyboardButton(text=LANG_RU_BUT)],
        [KeyboardButton(text=LANG_EN_BUT)]         
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        

        msg = await message.answer(
             config.LANG_RU["Select_Lang_err"] + "\n\n" +
             config.LANG_EN["Select_Lang_err"] + "\n\n" +
             config.LANG_UZ["Select_Lang_err"] + "\n\n" 
             , reply_markup=keyboard
        )
         
        
        
        await AddMessToRemove(msg)
        await state.set_state(ClientState.LANG_SELECTION)



@form_router.message(ClientState.LANG_SELECTION)
async def after_lang_sel_handler(message: Message, state: FSMContext) -> None:
        
        if message.text != LANG_EN_BUT and message.text != LANG_UZ_BUT and message.text != LANG_RU_BUT:
         
          await AddMessToRemove(message)
          await RemoveMessages()
          await lang_sel_handler(message, state ) 
          return
        



        # current_state = await state.get_state()
        # logging.info("e %r", current_state)
        data = await state.update_data(LANG_SELECTION=message.text)
        # data1 =  await state.get_data()
        # logging.info( data1["LANG_SELECTION"])
        await state.set_state(ClientState.MAIN_MENU)
        #await message.answer("", reply_markup=ReplyKeyboardRemove())
 
        await main_menu_handler(message, state)
        
    


@form_router.message(ClientState.MAIN_MENU)
async def main_menu_handler(message: Message, state: FSMContext) -> None:
    
    Option_location_str = await Translate_Message("Option_location", state)
    Option_cabinet_str =  await Translate_Message("Option_cabinet", state)
    Option_language_str = await Translate_Message("Option_language", state)
    Option_select_message_str = await Translate_Message("Option_select_message", state)
    

    await RemoveMessages()

    if message.text == Option_location_str:   
       await location_handler(message, state) 
       await message.delete()
       #return
    
    if message.text == Option_language_str:
       await state.clear()
       #await state.set_state(ClientState.START_MESS)
       await state.set_state(ClientState.LANG_SELECTION) 
       await after_lang_sel_handler(message, state)   
       return
 
    if message.text == Option_cabinet_str:
       #await state.clear()
       await state.set_state(ClientState.PERS_CAB_AUTH)
       await pers_cab_auth_handler(message, state) 
       return

    kb = [
        [KeyboardButton(text=Option_location_str)],
        [KeyboardButton(text=Option_cabinet_str)],
        [KeyboardButton(text=Option_language_str)]         
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    
  

    #current_state = await state.get_state()

    #if not current_state is ClientState.MAIN_MENU:
    msg = await message.answer(Option_select_message_str, reply_markup=keyboard)
    
  
    await AddMessToRemove(message)
    await RemoveMessages()
    
    await state.set_state(ClientState.MAIN_MENU) 
    await AddMessToRemove(msg)
    



@form_router.message(ClientState.MAIN_MENU_LOCATION)
async def loc_handler(message: Message, state: FSMContext) -> None:
    await  message.delete()

async def location_handler(message: Message, state: FSMContext) -> None:
    
   await state.set_state(ClientState.MAIN_MENU_LOCATION)
   
   msg = await Translate_Message("Location1_Mess", state)
   location = await Translate_Message("Location1", state) 

   msg1 = await message.answer(msg, parse_mode=ParseMode.HTML)
   #await msg1.reply_location(location[0], location[1])
   await message.answer_location(location[0], location[1])
   await state.set_state(ClientState.MAIN_MENU)
 
   
   
 
@form_router.message(ClientState.PERS_CAB_AUTH)
 
 
async def pers_cab_auth_handler(message: Message, state: FSMContext) -> None:
    
    cancel_str = await Translate_Message("Cancel", state)
    Pers_area_hello_str = await Translate_Message("Pers_area_hello", state)
    Pers_area_scan_qr_str = await Translate_Message("Pers_area_scan_qr", state)

    if message.text == cancel_str:
       await state.set_state(ClientState.MAIN_MENU) 
       await RemoveMessages()
       await main_menu_handler(message, state) 
       return

 
    kb = [
        
        [KeyboardButton(text=Pers_area_scan_qr_str)],
        [KeyboardButton(text=cancel_str)]       
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    msg = await message.answer(Pers_area_hello_str, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await AddMessToRemove(msg)
    
    
    await state.set_state(ClientState.PERS_CAB_AUTH)
    await AddMessToRemove(message)
      
   
  
 

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls


    
    dp.include_router(form_router)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main()) 