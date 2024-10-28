import sys, re, io, base64, logging, asyncio, config, http1c
from os import getenv
from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart , StateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputMediaDocument, ReplyKeyboardRemove, InlineKeyboardMarkup , InlineKeyboardButton, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types.input_file import FSInputFile, BufferedInputFile
from aiogram.utils.deep_linking import decode_payload
# from aiogram.methods.delete_message import DeleteMessage
 
# QR Code reader
import numpy as np
import cv2
from qreader import QReader



# Create a QReader instance
qreader = QReader()


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
#from AiogramStorages.storages import PGStorage

# PG_PASS = getenv("PG_PASS")
# storage = PGStorage(username='postgres', password=PG_PASS, db_name='zarmedbot_db')  
# dp = Dispatcher(bot, storage=storage)
# ------------------------------------------------------------
 

# Credentials
# Bot token can be obtained via https://t.me/BotFather
#TOKEN = config.TELEGRAM_BOT_TOKEN
TOKEN = getenv("BOT_TOKEN")
ONEC_USER = getenv("ONEC_USER")
ONEC_PASS = getenv("ONEC_PASS")

# All handlers should be attached to the Router (or Dispatcher)
form_router = Router()
dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

messages_del = []

 

# FSM Class
class ClientState(StatesGroup):
    LANG_SELECTION = State()
    START_MESS = State()
    MAIN_MENU = State()
    MAIN_MENU_LOCATION = State()
    PERS_CAB_AUTH = State()
    PERS_CAB_AUTH_BEGIN = State()
     


# Text translation 
async def  TranslateMessage(MessageName: str, state: FSMContext) -> any:

    try:
        data =  await state.get_data() 
        
        if data == None:
          return
        
        lang = data["LANG_SELECTION"]  
        
        if lang == config.LANG_EN_BUT:
         return config.LANG_RU_EN_UZ[MessageName][1]
            
        if lang == config.LANG_UZ_BUT:
         return config.LANG_RU_EN_UZ[MessageName][2]
        
        if lang == config.LANG_RU_BUT:
         return config.LANG_RU_EN_UZ[MessageName][0]
     
    except:
        logging.error("Unable to translate the message: " + MessageName)
        return "Message translation error."    



# Replace Windows/Linux filesystem reserved symbols
def repl_forb(string):
  forbidden_char={'<': ' ',
                 '>': ' ',
                 ':': '.',
                 '"': ' ',
                 '/': ' ',
                 '\\': ' ',
                 '|': ' ',
                 '#': ' ',
                 '?': ' ',
                 '*': ' '
                 }


  for   rep in forbidden_char:
                 string=string.replace(rep,forbidden_char[rep])
  if len(string) > 50:
      string=string[0:50]+" "

  return string




async def RemoveMessages():
    tt = []
    
    for i in messages_del:
      tt.append(i[1])
      chat_id = i[0]
    #   try:
          
    #      await bot.delete_message(chat_id=i[0],message_id=i[1])
    #   except:
    #       logging.error("Unable to delete message: "  + str(i[0]) + " - " + str(i[1]) )
    #       pass 
    try: 
      await bot.delete_messages(chat_id, tt)
    except:
        logging.error("Unable to delete message: " ) 
        pass
    messages_del.clear()

async def AddMessToRemove(messages: list[Message]):
    for message in messages:
     if message != None:
       messages_del.append([message.chat.id, message.message_id])
 
 
 
 
 
 
 
 
"""
This handler receives messages with `/start` command
"""

@form_router.message(CommandStart(deep_link=True, ignore_case=True,deep_link_encoded=False))
async def command_start_handler(message: Message, command: Command, state = FSMContext) -> None:
    
    await state.clear()
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
 
    if command != None:
     args = command.args
    else:
     args = ""
     
    
    
    #payload = decode_payload(args)
    #await message.answer(f"Your payload: {payload}")

 
    logging.info("The user with name '" + message.from_user.full_name + "' has started the bot with params: " + args)
 
    msgtxt = \
    config.LANG_RU_EN_UZ["Hello"][0]+f"{html.bold(message.from_user.full_name)}! " + config.LANG_RU_EN_UZ["Hello_mess"][0] + '\n\n' + \
    config.LANG_RU_EN_UZ["Hello"][1]+f"{html.bold(message.from_user.full_name)}! " + config.LANG_RU_EN_UZ["Hello_mess"][1] + '\n\n' + \
    config.LANG_RU_EN_UZ["Hello"][2]+f"{html.bold(message.from_user.full_name)}! " + config.LANG_RU_EN_UZ["Hello_mess"][2] 
 
    await message.answer(msgtxt)
    await lang_sel_handler(message, state)  
    await state.set_state(ClientState.LANG_SELECTION)
  
   
     
async def CheckRestart(message: Message, state: FSMContext):
    if message.text == "/start":
         await command_start_handler(message, None, state)
         return

 
@form_router.message(ClientState.LANG_SELECTION)
async def lang_sel_handler_deleter(message: Message, state: FSMContext) -> None:
    await CheckRestart(message, state)
    await message.delete()
    
    
    
async def lang_sel_handler(message: Message, state: FSMContext) -> None:
       
    logging.info("lang selection handler ")
    
    inline_kb1 = InlineKeyboardMarkup(
                    inline_keyboard=[[
                        InlineKeyboardButton(text=config.LANG_UZ_BUT, callback_data=config.LANG_UZ_BUT),
                        InlineKeyboardButton(text=config.LANG_RU_BUT, callback_data=config.LANG_RU_BUT),
                        InlineKeyboardButton(text=config.LANG_EN_BUT, callback_data=config.LANG_EN_BUT)
                        ]]
                    )
 
    messtxt = config.LANG_RU_EN_UZ["Select_Lang_err"][0] + "\n" + \
                  config.LANG_RU_EN_UZ["Select_Lang_err"][1] + "\n" + \
                  config.LANG_RU_EN_UZ["Select_Lang_err"][2] + "\n" 
        
    await message.answer(messtxt, reply_markup=inline_kb1)
    await state.set_state(ClientState.LANG_SELECTION)
    
            


 


@form_router.message(ClientState.MAIN_MENU)
async def main_menu_handler_deleter(message: Message, state: FSMContext) -> None:
    await CheckRestart(message, state)
    await message.delete()

async def main_menu_handler(message: Message, state: FSMContext) -> None:
    

    
    Option_location_str = await TranslateMessage("Option_location", state)
    Option_cabinet_str =  await TranslateMessage("Option_cabinet", state)
    Option_language_str = await TranslateMessage("Option_language", state)
 


    inline_kb1 = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text=Option_location_str, callback_data=Option_location_str)],
                        [InlineKeyboardButton(text=Option_cabinet_str, callback_data=Option_cabinet_str)],
                        [InlineKeyboardButton(text=Option_language_str, callback_data=Option_language_str)]
                        ]
                    )
                   
 
    await message.answer(await TranslateMessage("Option_select_message", state), reply_markup=inline_kb1)
    await state.set_state(ClientState.MAIN_MENU)

 
 
# Location handler
@form_router.message(ClientState.MAIN_MENU_LOCATION)
async def loc_handler(message: Message, state: FSMContext) -> None:
    
    await  message.delete()

async def location_handler(message: Message, state: FSMContext) -> None:
  
   await state.set_state(ClientState.MAIN_MENU_LOCATION) 
   location = await TranslateMessage("Location1", state) 
   await message.answer_location(location[0], location[1])
   await message.answer(await TranslateMessage("Location1_Mess", state), parse_mode=ParseMode.HTML)
   await state.set_state(ClientState.MAIN_MENU)
 
   
   
   
   
# Authorization begin
# @form_router.message(ClientState.PERS_CAB_AUTH_BEGIN)

async def pers_cab_auth_begin_handler(message: Message, state: FSMContext) -> None:
 
    if message.text == "/start":
        await command_start_handler(message, None, state)
        return
 
    
    
    photo = FSInputFile("res/qr.jpg")
    msg1 = await message.answer_photo(photo=photo, caption=await TranslateMessage("Pers_area_hello", state))
    
    
    
    inline_kb1 = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text=await TranslateMessage("Cancel", state), callback_data=await TranslateMessage("Cancel", state))]
                
                        ]
                    )
                   
 
     
    msg = await message.answer(await TranslateMessage("Pers_area_cancel_button", state), reply_markup=inline_kb1, parse_mode=ParseMode.HTML)
    
    await AddMessToRemove([msg, msg1, message])
    
 
 
 
@form_router.message(ClientState.PERS_CAB_AUTH)

 
async def pers_cab_auth_handler(message: Message, state: FSMContext) -> None:
    
 
    
    userId = ''
    password = ''
    
    if message.photo:    

     #try:
       img_stream = io.BytesIO()
       pid =  message.photo[-1].file_id
       await bot.download(pid, img_stream)
       img_stream.seek(0)
            
       # read image as an numpy array 
       img_array = np.asarray(bytearray(img_stream.read()), dtype="uint8") 
        
       # use imdecode function 
       img = cv2.imdecode(img_array, cv2.COLOR_BGR2RGB) 

       # Get the image that contains the QR code
       image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

       # Use the detect_and_decode function to get the decoded QR data
       #qrCodeDetector = cv2.QRCodeDetector()
       #decodedText, points, _ = qrCodeDetector.detectAndDecode(image)
       decoded_texts = qreader.detect_and_decode(image=image) 
       
       if len(decoded_texts)  > 0 and not decoded_texts[0] is None:
         first_found_qr = str(decoded_texts[0])
        #  await message.answer(first_found_qr)
         patterns = re.findall(r"start=[0-9]{8}:[0-9]{8}", first_found_qr)
        
         
         if len(patterns) == 0:
                await message.answer(await TranslateMessage("Pers_area_wrong_qr", state))
         else:
                first_found_qr  = first_found_qr.split("?start=")[1]  
                userId = first_found_qr.split(":")[0]
                password = first_found_qr.split(":")[1]
                # await message.answer("UserId/Password: " + userId + "/" + password)
 
       else:
         await message.answer(await TranslateMessage("Pers_area_nota_qr",state))
         return
         
                 
    #    await message.delete()
    #    return      
     
     #except:
        #logging.error("An exception occurred during qr decoding.") 
    
    elif len(re.findall(r"^ {0,}[0-9]{8} {1,}[0-9]{8} {0,}$", message.text)) > 0 :
        loginpasspattern = str(re.findall(r"^ {0,}[0-9]{8} {1,}[0-9]{8} {0,}$", message.text)[0])
        userId = loginpasspattern.split()[0]
        password = loginpasspattern.split()[1]
        # await message.answer(userId+" "+password)
         
    else:
        await message.answer(await TranslateMessage("Pers_area_auth_wrong_input", state))
        return
        
        
        
    
    msg1 = await message.answer(await  TranslateMessage("Pers_area_auth_inprogress", state)) 

    await AddMessToRemove([msg1])
    
    result = http1c.DBRequest('appapi/getApp?userid=' + userId+ '&ucode=' + password)
    print(result)
    if result[0] != 200:
        if result[0] == 401:
          await message.answer(await TranslateMessage("Pers_area_auth_wrong_auth_data", state))
          return
        else:
          await message.answer(await TranslateMessage("General_err_un", state))
          return
    
    await RemoveMessages()
    buttons = []
        
    Appdates = result[1]["AppDates"]
                        
    for x in range(0, len(Appdates), 2):
        row = []
        row.append(InlineKeyboardButton(text=Appdates[x].get("Date"), callback_data=Appdates[x].get("Date")+'|'+userId+'|'+password  ))                 
        if len(Appdates) >= (x+2):                    
                    row.append(InlineKeyboardButton(text=Appdates[x+1].get("Date"), callback_data=Appdates[x+1].get("Date")+'|'+userId+'|'+password ))
        buttons.append( row)

    
    buttons.append([
        InlineKeyboardButton(
            text=await TranslateMessage("Cancel", state), 
            callback_data=await TranslateMessage("Cancel", state)
            )
        ])
    inline_kb1 = InlineKeyboardMarkup(inline_keyboard=buttons)
        

    msg2 = await message.answer("Выберите дату посещения: ", reply_markup=inline_kb1)
    await AddMessToRemove([msg1,msg2])

    
    
  


#result = DBRequest('appapi/getApp?userid=00001411&ucode=57084919')
#result = http1c.DBRequest('appapi/getAppD?appdata=03.06.2024&userid=00001411&ucode=57084919')
#result = DBRequest('appapi/getSet')
 



# Callback handler

@form_router.callback_query()
async  def call_handler(message: CallbackQuery, state: FSMContext):
    
    chatid = message.message.chat.id
 
    
    if await state.get_state() == None:
       print(message.message)
       await command_start_handler(message.message, None, state) 
       return
    
    if await state.get_state() == ClientState.MAIN_MENU: 
    
        if message.data == await TranslateMessage("Option_location", state): 
            await location_handler(message.message, state)  
            await main_menu_handler(message.message, state)
            await state.set_state(ClientState.MAIN_MENU) 
            await message.message.delete()
            return
        
        if message.data == await TranslateMessage("Option_language", state): 
            await lang_sel_handler(message.message, state)    
            await state.set_state(ClientState.LANG_SELECTION) 
            await message.message.delete()
            return
        
        if message.data == await TranslateMessage("Option_cabinet", state): 
            await pers_cab_auth_begin_handler(message.message, state)    
            # await state.set_state(ClientState.PERS_CAB_AUTH_BEGIN) 
            await state.set_state(ClientState.PERS_CAB_AUTH)
            await message.message.delete()
            return
    
   

        
    if await state.get_state() == ClientState.LANG_SELECTION:
    
        if message.data != config.LANG_EN_BUT and message.data != config.LANG_UZ_BUT and message.data != config.LANG_RU_BUT: 
          await  message.message.delete()
          return
        
 
        await state.update_data(LANG_SELECTION=message.data)
        # data1 =  await state.get_data()
        # logging.info( data1["LANG_SELECTION"])
        
        await main_menu_handler(message.message, state)
 
        await state.set_state(ClientState.MAIN_MENU) 
        await  message.message.delete()
        return
    
    
    if await state.get_state() == ClientState.PERS_CAB_AUTH:
        
        if message.data == await TranslateMessage("Cancel", state): 
                await main_menu_handler(message.message, state)
                await state.set_state(ClientState.MAIN_MENU) 
                #await message.message.delete()
                await RemoveMessages()
                return
            
        reqdata = message.data.split("|")  
                
        result = http1c.DBRequest('appapi/getAppD?appdata=' + str(reqdata[0]) + '&userid='+ str(reqdata[1]) + '&ucode='+ str(reqdata[2]))
        
        
        print(result)
        if result[0] == 200:
            media_group = list()
            # await bot.send_message(chatid, await TranslateMessage("Pers_area_appointment_yourapps",state) + " " + str(reqdata[0]))
            count = 1
            for app in result[1]["Apps"]:
                
                
                for att in app["attachments"]:
                    bindata = base64.b64decode(att["base64data"])
                    attnamefull = repl_forb(app["items"] + " "  ) + str(reqdata[0]) + "." + str(count) + att["attext"]
                    
                    file = BufferedInputFile(bindata,attnamefull)
              
                    # caption = str(await TranslateMessage("Pers_area_appointment_yourapps",state) + " " + str(reqdata[0])).replace('(N)', str(count))
                    media_group.append(InputMediaDocument(media=file ))
                    count = count+1
                    
            await bot.send_media_group(chat_id=chatid,media=media_group, request_timeout=config.HTTP_TIMEOUT)   
        elif result[0] == 204: 
            await bot.send_message(chatid, str(await TranslateMessage("Pers_area_appointment_nodata",state)).replace("(D)", str(reqdata[0])) )
        else:
            await bot.send_message(chatid, await TranslateMessage("General_err_un",state) )
        
  
     
        
        
        
        
        
        
        
 #Restarting the bot if the state is None
@form_router.message(StateFilter(None))

# @form_router.callback_query(StateFilter(None))
async def restart_handler(message: Message,  state: FSMContext) -> None:
  
  await command_start_handler(message, None, state)
  
  
  
  
  
  
 
# Main function 
async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
 
    dp.include_router(form_router)

    # And the run events dispatching
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main()) 