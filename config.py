

# 1C Settings
HTTP_TIMEOUT = 10
ONEC_IP = '192.168.1.42'
ONEC_DB = 'mis'

# BOT Settings
LANG_EN_BUT = "🇬🇧 English"
LANG_UZ_BUT = "🇺🇿 O'zbek"
LANG_RU_BUT = "🇷🇺 Русский" 
PHONE_STR = "\n\n1063\n\n+998557021063\n\n\n"

LANG_RU_EN_UZ =  {
  
  "Hello": ["Здравствуйте 👋,",
            "Hello 👋,",
            "Assalomu aleykum! 👋,"],
  
  "Hello_mess": [" \nВас приветствует бот клиники Zarmed Pratiksha!",
                 " \nZarmed Pratiksha clinic bot welcomes you!",
                 " \nZarmed Pratiksha klinikasi botiga xush kelibsiz!"],
  
  "Select_Lang_err": ["Пожалуйста, выберите язык!",
                      "Please, select your language!",
                      "Iltimos, tilni tanlang!"],
  
  "Option_location": ["📞 Контакты и локации",
                      "📞 Contacts and locations",
                      "📞 Kontaktlar va manzillar"],
  
  "Option_cabinet": ["👤 Анализы и приемы врача",
                     "👤 Lab tests and visits",
                     "👤 Test natijalari va shifokor qabuliga"],
  
  "Option_language": ["🇷🇺 Выбрать язык",
                      "🇬🇧 Select language",
                      "🇺🇿 Tilni tanlang"],
  
  "Option_select_message": ["Выберите действие:",
                            "Select an option:",
                            "Amalni tanlang:"],
  
  
  "Location1_Mess": ["📗 <b>Адрес центральной клиники:</b>\nСамарканд, Самаркандская область, Ул. Исаева 16, 140100\n\n<b>Телефон:</b>"+PHONE_STR,
                     "📗 <b>Address of the head clinic:</b>\nSamarqand, Samarqand district, Isayev Str 16, 140100\n\n<b>Telephone:</b>"+PHONE_STR,
                     "📗 <b>Markaziy klinika manzili:</b>\nSamarqand shahar, Samarqand viloyati, Isaeva ko`chasi, 16, 140100\n\n<b>Telefon:</b>"+PHONE_STR],
  
  "Location1": [[39.648779, 66.946713],
                [39.648779, 66.946713],
                [39.648779, 66.946713]],
  
  "Pers_area_hello": ["🪪 Данный раздел позволяет получить результаты ваших анализов и приемов врачей.\nДля входа сфотографируйте qr-код, либо введите идентификатор пользователя (синее поле) и код (красное поле) в виде: \n<b>12345678 12345678</b>",
                      "🪪 In this section you can get the results of tests and doctor's visits.To enter, take a picture of the qr code or enter your user ID (blue field) and code (red field) as shown in the example: \n<b>12345678 12345678</b>",
                      "🪪 Ushbu boʻlim sizga test natijalari va shifokor qabuliga borish imkonini beradi.\nKirish uchun QR kodni suratga oling yoki foydalanuvchi identifikatorini (koʻk maydon) va kodni (qizil maydon) quyidagi shaklga kiriting: \n<b>12345678 12345678</b>"],
                      
  "Pers_area_cancel_button": ["Для выхода нажмите кнопку отмена.",
                        "Press cancel button to exit.",
                        "Chiqish uchun bekor qilish tugmasini bosing."],
  
  "Pers_area_wrong_qr": ["Этот QR код не является правильным кодом авторизации.",
                          "This QR code is not a valid authorization code.",
                          "Bu QR kodi to`g`ri avtorizatsiya kodi emas."],
  
  "Pers_area_nota_qr": ["QR не обнаружен.",
                        "QR code not found.",
                        "QR topilmadi."],
  
  "Pers_area_auth_inprogress": ["Попытка авторизации... ⏳",
                                "Authorization attempt... ⏳",
                                "Tizimga kirishga urinish... ⏳"],
  
  "Pers_area_auth_wrong_input": ["Неправильный ввод. Попробуйте еще раз.",
                                  "Incorrect input. Try again.",
                                  "Noto`g`ri kiritish. Qayta urinib ko'ring."],
  
  
  "Pers_area_auth_wrong_auth_data": ["Данные пользователя неверны или пользователь не найден. Попробуйте еще раз.",
                                     "The user data is incorrect or the user is not found. Try again.",
                                     "Foydalanuvchi ma'lumotlari noto'g'ri yoki foydalanuvchi topilmadi. Qayta urinib ko'ring."],
  
    
  "Pers_area_appointment_select_no_app_for_date": ["За текущий период посещений не найдено. Попробуйте позже, либо обратитесь по номерам:"+PHONE_STR,
                                                   "No visits were found for the current period. Try again later, or contact us by phone:"+PHONE_STR,
                                                   "Joriy davr uchun tashriflar topilmadi. Keyinroq qayta urinib ko'ring yoki raqamlarga qo'ng'iroq qiling:"+PHONE_STR],
  
  
  "Pers_area_appointment_select_date_mes": ["Ваши посещения за последние (D) дней.\nНажимайте кнопку нужной даты, чтобы проверить готовность анализов.",
                                            "Your visits for the last (D) days.\nTap the date button to see if your test results are available.",
                                            "Oxirgi (D) kunlardagi tashriflaringiz.\nTahlillar tayyorligini tekshirish uchun kerekli sana tugmasini bosing."],
  
  "Pers_area_appointments_not_ready": ["❗Неготовые исследования за дату (D):",
                                       "❗Unready tests for the date (D):",
                                       "❗Sana uchun tugallanmagan tadqiqotlar (D):"],
     
  "Pers_area_appointments_ready":     ["✅ Готовые исследования за дату (D)",
                                       "✅ Ready tests for the date (D)",
                                       "✅ Sana uchun tugallangan tadqiqotlar (D)"],
     
  
  "Pers_area_appointment_nodata": ["За дату (D) документов не обнаружено. Попробуйте позже, либо обратитесь по номерам:"+PHONE_STR,
                                   "No documents were found for date (D). Try again later or contact us by phone:"+PHONE_STR,
                                   "(D) sana uchun hech qanday hujjat topilmadi. Keyinroq qayta urinib ko'ring yoki raqamlarga qo'ng'iroq qiling:"+PHONE_STR],
   
 
  "Cancel": ["❌ Отмена",
             "❌ Cancel",
             "❌ Bekor qilish"],
  
  
  "General_err_un": ["Данная функция в данный момент недоступна.",
                     "This feature is not available at this time.",
                     "Bu xususiyat hozirda mavjud emas."]
}


 