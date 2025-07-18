import sys, re, io, base64, logging, asyncio, config, http1c
from os import getenv
from aiogram.utils.backoff import Backoff, BackoffConfig
from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart , StateFilter, CommandObject
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputMediaDocument, ReplyKeyboardRemove, InlineKeyboardMarkup , InlineKeyboardButton, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types.input_file import FSInputFile, BufferedInputFile
#from aiogram.utils.deep_linking import decode_payload
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
#TOKEN = getenv("BOT_TOKEN")
#bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot = None

 

# All handlers should be attached to the Router (or Dispatcher)
form_router = Router()
dp = Dispatcher()



messages_del = {}
AllUsersIds = {} 

# FSM Class
class ClientState(StatesGroup):
    LANG_SELECTION = State()
    START_MESS = State()
    MAIN_MENU = State()
    MAIN_MENU_LOCATION = State()
    PERS_CAB_AUTH = State()
    
     
# Get settings
async def GetSettings():
       result = http1c.DBRequest('appapi/getSet')
       logging.info("Trying to get token. " + str(result))
       if result[0] == 200:
           global bot
           bot = Bot(token=result[1]["TgToken"],
                     default=DefaultBotProperties(parse_mode=ParseMode.HTML))
 



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
        return "Message translation error"     



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




async def RemoveMessages(Chatid):
 
    try:
        
     MessToDel = messages_del.get(Chatid)
     if MessToDel == None:
        return 
     await bot.delete_messages(Chatid, MessToDel)
     messages_del.pop(Chatid)
       
    except  Exception as error:
        logging.error("Unable to delete message: " , error ) 
        messages_del.pop(Chatid)
        pass
   




async def AddMessToRemove(messages: list[Message]):
    try:
        for message in messages:
            if message != None:
                
               ChatMessagesToDel: list
               ChatMessagesToDel = messages_del.get(message.chat.id)
               if ChatMessagesToDel == None:
                   messages_del.update({message.chat.id:[message.message_id]})
               else:
                  ChatMessagesToDel.append(message.message_id)  
                  messages_del.update({message.chat.id:ChatMessagesToDel})
    except:
        logging.info("Error adding message to remove list " + str([message.chat.id, message.message_id]))
        
 
 
 
     
async def CheckRestart(message: Message, state: FSMContext):
    
    if message.text == "/start" or await state.get_state() == None:
          if AllUsersIds.get(message.from_user.id) != None:
             AllUsersIds.pop(message.from_user.id)
          
          await command_start_handler(message, None, state)
          return True

  
         
#Restart the bot if the state is None
@form_router.message(StateFilter(None)) 
async def restart_handler(message: Message,  state: FSMContext) -> None:
  await command_start_handler(message, None, state)
  
 
# This handler receives messages with `/start` command
@form_router.message(CommandStart(deep_link=True))
async def command_start_handler(message: Message, command: CommandObject, state = FSMContext) -> None:
    
    await state.clear()
    
    
    if command != None and command.args != "":
       AllUsersIds.update({message.from_user.id:str(command.args)})
       logging.info("The user with name '" + message.from_user.full_name + "' has started the bot with params: " + command.args)
 
 
    #payload = decode_payload(args)
    #await message.answer(f"Your payload: {payload}")
 
    msgtxt = \
    config.LANG_RU_EN_UZ["Hello"][0]+f"{html.bold(message.from_user.full_name)}! " + config.LANG_RU_EN_UZ["Hello_mess"][0] + '\n\n' + \
    config.LANG_RU_EN_UZ["Hello"][1]+f"{html.bold(message.from_user.full_name)}! " + config.LANG_RU_EN_UZ["Hello_mess"][1] + '\n\n' + \
    config.LANG_RU_EN_UZ["Hello"][2]+f"{html.bold(message.from_user.full_name)}! " + config.LANG_RU_EN_UZ["Hello_mess"][2] 
 
    await message.answer(msgtxt)
    await state.set_state(ClientState.LANG_SELECTION)
    await lang_sel_handler(message, state)  
    
  
   

 # Language selection handler
@form_router.message(ClientState.LANG_SELECTION)
async def lang_sel_handler_deleter(message: Message, state: FSMContext) -> None:
    await CheckRestart(message, state)
    await message.delete()
    
    
    
async def lang_sel_handler(message: Message, state: FSMContext) -> None:
 
    
    
    inline_kb1 = InlineKeyboardMarkup(
                    inline_keyboard=[[
                        InlineKeyboardButton(text=config.LANG_UZ_BUT, callback_data=config.LANG_UZ_BUT),
                        InlineKeyboardButton(text=config.LANG_RU_BUT, callback_data=config.LANG_RU_BUT),
                        InlineKeyboardButton(text=config.LANG_EN_BUT, callback_data=config.LANG_EN_BUT)
                        ]]
                    )
 
    messtxt =     config.LANG_RU_EN_UZ["Select_Lang_err"][0] + "\n" + \
                  config.LANG_RU_EN_UZ["Select_Lang_err"][1] + "\n" + \
                  config.LANG_RU_EN_UZ["Select_Lang_err"][2] + "\n" 
        
    msg = await message.answer(messtxt, reply_markup=inline_kb1)
    await state.set_state(ClientState.LANG_SELECTION)
    await RemoveMessages(message.chat.id)
    await AddMessToRemove([msg])
    
            


 

# Main menu handler
@form_router.message(ClientState.MAIN_MENU)
async def main_menu_handler_deleter(message: Message, state: FSMContext) -> None:
    if await CheckRestart(message, state): return
    await AddMessToRemove([message])
    await RemoveMessages(message.chat.id)
     

async def main_menu_handler(message: Message, state: FSMContext) -> None:
    
    if AllUsersIds.get(message.from_user.id) != None:
       AllUsersIds.pop(message.from_user.id)
   
    
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
    await RemoveMessages(message.chat.id)
    await state.set_state(ClientState.MAIN_MENU)

 
 
# # Location handler
# @form_router.message(ClientState.MAIN_MENU_LOCATION)
# async def loc_handler(message: Message, state: FSMContext) -> None:
#     await  message.delete()

async def location_handler(message: Message, state: FSMContext) -> None:
  
   await state.set_state(ClientState.MAIN_MENU_LOCATION) 
   location = await TranslateMessage("Location1", state) 
   await message.answer_location(location[0], location[1])
   await message.answer(await TranslateMessage("Location1_Mess", state), parse_mode=ParseMode.HTML)
#    await state.set_state(ClientState.MAIN_MENU)
 
   
   
   
   
# Authorization begin
# @form_router.message(ClientState.PERS_CAB_AUTH_BEGIN)

async def pers_cab_auth_begin_handler(message: Message, state: FSMContext) -> None:
 
     
    if await CheckRestart(message, state): return
    
    
   
    
    photo = FSInputFile("res/qr.jpg")
    msg1 = await message.answer_photo(photo=photo, caption=await TranslateMessage("Pers_area_hello", state))
    
    
    
    inline_kb1 = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text=await TranslateMessage("Cancel", state), callback_data=await TranslateMessage("Cancel", state))]
                
                        ]
                    )
                   
 
     
    msg = await message.answer(await TranslateMessage("Pers_area_cancel_button", state), reply_markup=inline_kb1, parse_mode=ParseMode.HTML)
    await RemoveMessages(message.chat.id)
    await AddMessToRemove([msg, msg1])
    
 
 
 # Authorization process
@form_router.message(ClientState.PERS_CAB_AUTH)

 
async def pers_cab_auth_handler(message: Message, state: FSMContext, origmess: Message = None) -> None:
    
    if await CheckRestart(message, state): return
    

    
    userId = ''
    password = ''
    
    buttons = []   
    buttons.append([
    InlineKeyboardButton(
        text=await TranslateMessage("Cancel", state), 
        callback_data=await TranslateMessage("Cancel", state)
        )
    ])
    inline_kb1 = InlineKeyboardMarkup(inline_keyboard=buttons)
           
    if origmess != None:
     UserId =  AllUsersIds.get(origmess.from_user.id)
     logging.error("Trying to authorize with "+UserId)
     if UserId != None:
           userId = UserId[0:8]
           password = UserId[8:16]
    

    
    elif  message.photo:    

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
         patterns = re.findall(r"start=[0-9]{16}", first_found_qr)
        
         
         if len(patterns) == 0:
                await message.answer(await TranslateMessage("Pers_area_wrong_qr", state))
                return
         else:
                first_found_qr  = first_found_qr.split("?start=")[1]  
                userId = first_found_qr[0:8]
                password = first_found_qr[8:16]
                 
       else:
         await message.answer(await TranslateMessage("Pers_area_nota_qr",state))
         return
         
 
     #except:
        #logging.error("An exception occurred during qr decoding.") 
    
    elif message != None and message.text != None and len(re.findall(r"^ {0,}[0-9]{8} {1,}[0-9]{8} {0,}$", message.text)) > 0 :
        loginpasspattern = str(re.findall(r"^ {0,}[0-9]{8} {1,}[0-9]{8} {0,}$", message.text)[0])
        userId = loginpasspattern.split()[0]
        password = loginpasspattern.split()[1]
        # await message.answer(userId+" "+password)
         
    else:
        msg =  await message.answer(await TranslateMessage("Pers_area_auth_wrong_input", state), reply_markup=inline_kb1)
        await AddMessToRemove([msg])
        return
        
    
    await RemoveMessages(message.chat.id) 
    
    result = http1c.DBRequest('appapi/getApp?userid=' + userId+ '&ucode=' + password)
     
    if result[0] != 200:
        if result[0] == 401:
          msg = await message.answer(await TranslateMessage("Pers_area_auth_wrong_auth_data", state),reply_markup=inline_kb1)
          await  AddMessToRemove([msg])
          return
        elif result[0] == 204:
          msg = await message.answer(await TranslateMessage("Pers_area_appointment_select_no_app_for_date", state),reply_markup=inline_kb1)
          return 
        else:
          msg = await message.answer(await TranslateMessage("General_err_un", state), reply_markup=inline_kb1)
          await AddMessToRemove([msg])
          return
    
    await RemoveMessages(message.chat.id)
    
    
  
    ldays = str(result[1]["Period"])
    Appdates = result[1]["AppDates"]
     
    buttons = []    
                        
    for x in range(0, len(Appdates), 2):
        row = []
        row.append(InlineKeyboardButton(text=Appdates[x]["Date"], callback_data=Appdates[x]["Date"]+'|'+userId+'|'+password  ))                 
        if len(Appdates) >= (x+2):                    
                    row.append(InlineKeyboardButton(text=Appdates[x+1]["Date"], callback_data=Appdates[x+1]["Date"]+'|'+userId+'|'+password ))
        buttons.append(row)

    
    buttons.append([
    InlineKeyboardButton(
        text=await TranslateMessage("Cancel", state), 
        callback_data=await TranslateMessage("Cancel", state)
        )
    ])
    inline_kb1 = InlineKeyboardMarkup(inline_keyboard=buttons)
           
        

    msg2 = await message.answer(str(await TranslateMessage("Pers_area_appointment_select_date_mes", state)).replace("(D)",ldays), reply_markup=inline_kb1)
    await AddMessToRemove([msg2])
    









# Get documents 
async def pers_cab_auth_get_app_handler(message: CallbackQuery, state: FSMContext ) -> None:
        
         
        
        
    try: 
        chatid = message.message.chat.id
        reqdata = message.data.split("|") 
               
        result = http1c.DBRequest('appapi/getAppD?appdata=' + str(reqdata[0]) + '&userid='+ str(reqdata[1]) + '&ucode='+ str(reqdata[2]))
        
        
        
        if result[0] == 200:


          try:
            if int(result[1]["TotalCount"]) > 0:
             media_group = list()
             count = 1
             ready_mess = str(await TranslateMessage("Pers_area_appointments_ready",state)).replace("(D)", str(reqdata[0]))
             
             await bot.send_message(chatid, ready_mess) 
             
             for app in result[1]["Apps"]:
                 for att in app["attachments"]:
                    bindata = base64.b64decode(att["base64data"])
                    attnamefull = repl_forb(app["items"] + " "  ) + str(reqdata[0]) + "." + str(count) + att["attext"]
                    
                    file = BufferedInputFile(bindata,attnamefull)
               
                    media_group.append(InputMediaDocument(media=file))
                    count = count+1
                   
                           
             await bot.send_media_group(chat_id=chatid,media=media_group, request_timeout=config.HTTP_TIMEOUT) 
            
            if int(result[1]["TotalCountNotReady"]) > 0: 
                count = 1
                not_ready_mess = str(await TranslateMessage("Pers_area_appointments_not_ready",state)).replace("(D)", str(reqdata[0]))
                for notready in result[1]["LabAppsNotReady"]:
                   not_ready_mess = not_ready_mess + "\n" + str(count) + ") " + notready["item"]
                   count = count+1 
                await bot.send_message(chatid, not_ready_mess) 
          except:
              await bot.send_message(chatid, await TranslateMessage("General_err_un",state) )
        elif result[0] == 204: 
            await bot.send_message(chatid, str(await TranslateMessage("Pers_area_appointment_nodata",state)).replace("(D)", str(reqdata[0])) )
        else:
            await bot.send_message(chatid, await TranslateMessage("General_err_un",state) )
    except:
        await bot.send_message(chatid, await TranslateMessage("General_err_un",state) )
        
        

# Callback handler

@form_router.callback_query()
async  def call_handler(message: CallbackQuery, state: FSMContext):
    
    
 
    
    if await CheckRestart(message.message, state): return
    
    if await state.get_state() == ClientState.MAIN_MENU: 
    
        if message.data == await TranslateMessage("Option_location", state):
            await AddMessToRemove([message.message]) 
            await location_handler(message.message, state) 
            await state.set_state(ClientState.MAIN_MENU) 
            await main_menu_handler(message.message, state)
            return
        
        if message.data == await TranslateMessage("Option_language", state): 
            await AddMessToRemove([message.message])
            await state.set_state(ClientState.LANG_SELECTION) 
            await lang_sel_handler(message.message, state)    
            return
        
        if message.data == await TranslateMessage("Option_cabinet", state): 
            await AddMessToRemove([message.message])
            await state.set_state(ClientState.PERS_CAB_AUTH) 
            await pers_cab_auth_begin_handler(message.message, state)    
            return
    
   

        
    if await state.get_state() == ClientState.LANG_SELECTION:
    
        if message.data != config.LANG_EN_BUT and message.data != config.LANG_UZ_BUT and message.data != config.LANG_RU_BUT: 
          await AddMessToRemove([message.message])
          return
        
 
        await state.update_data(LANG_SELECTION=message.data)
        # data1 =  await state.get_data()
        # logging.info( data1["LANG_SELECTION"])
        UserId = AllUsersIds.get(message.from_user.id)
        if UserId != None:
           await state.set_state(ClientState.PERS_CAB_AUTH) 
           await pers_cab_auth_handler(message.message, state, message) 
           return
        
        
        await state.set_state(ClientState.MAIN_MENU) 
        await AddMessToRemove([message.message])
        await main_menu_handler(message.message, state)
        return
    
    
    if await state.get_state() == ClientState.PERS_CAB_AUTH:
        
        if message.data == await TranslateMessage("Cancel", state): 
                await state.set_state(ClientState.MAIN_MENU) 
                if AllUsersIds.get(message.from_user.id) != None:
                   AllUsersIds.pop(message.from_user.id)
                await AddMessToRemove([message.message])
                await main_menu_handler(message.message, state)
                return
        else:
            await pers_cab_auth_get_app_handler(message, state)
            return
      
       
     
  
 
# Main function 
async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    
    await GetSettings()
    if bot == None:
        logging.error("Cannot start bot (cannot get Token from server)")
        return
    
    dp.include_router(form_router)
    
    bk = BackoffConfig(min_delay=0.5, max_delay=2.0, factor=1.3, jitter=0.1)
    
    # And the run events dispatching
    await dp.start_polling(bot, polling_timeout=10 , backoff_config=bk)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main()) 