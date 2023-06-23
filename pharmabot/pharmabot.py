# from telegram import Update, Bot
# from telegram.ext import Updater, CommandHandler, CallbackContext
# from geopy.distance import geodesic
# import sqlite3
# import telegram

# #db = sqlite3.connect("./farmacie.db")

# #with open("token.txt", "r") as f:
# #    TOKEN = f.read()
# #    print(TOKEN)

# #def main():
# #    app = ApplicationBuilder().token(TOKEN).build()
# #    app.add_handler(CommandHandler("start", start))
# #    app.add_handler(CommandHandler("FarmaciaVicina", get_nearest_pharma))

# #async def hello_funct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #    hello_var = update.effective_user.first_name
# #    await update.message.reply_text("Hello %s" % hello_var)

# #async def start_funct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #        hello_var = update.effective_user.first_name
# #        await update.message.reply_text("Ciao %s! Sono PharmaBot, ho la funzione di aiutarti a scegliere la farmacia ideale e più conveniente per te! Clicca uno dei tasti qui sotto per selezionare una funzione" %hello_var)


# def main() -> None:
#     def main() -> None:
#         TOKEN = "5643203403:AAEjSi-VlOLREODuq60Tm19wyjPmhHBpvjs"
#         bot = telegram.Bot(token=TOKEN)
#         bot._request.required_connection_pool_size = 16  # Set connection pool size directly on the bot instance
#         updater = Updater(bot=bot)
#         dispatcher = updater.dispatcher

#         start_handler = CommandHandler("start", start)
#         get_nearest_pharma_handler = CommandHandler("FarmaciaVicina", get_nearest_pharma)

#         dispatcher.add_handler(start_handler)
#         dispatcher.add_handler(get_nearest_pharma_handler)

#         updater.start_polling()
#         updater.idle()

# def start(update: Update, context: CallbackContext) -> None:
#     context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter your address.")

# def get_nearest_pharma(update: Update, context: CallbackContext) -> None:
#     try:
#         user_address = update.message.text

#         # Retrieve pharmacy addresses from the database
#         pharmacy_addresses = get_pharmacy_addresses()

#         # Calculate distances between user's address and each pharmacy
#         distances = []
#         for pharmacy_address in pharmacy_addresses:
#             distance = geodesic(user_address, pharmacy_address).kilometers
#             distances.append(distance)

#         if distances:
#             min_distance = min(distances)
#             nearest_pharmacy_index = distances.index(min_distance)
#             nearest_pharmacy = pharmacy_addresses[nearest_pharmacy_index]
#             update.message.reply_text(f"Nearest pharmacy address: {nearest_pharmacy}")
#         else:
#             update.message.reply_text("No nearby pharmacies found.")
#     except ValueError:
#         update.message.reply_text("Invalid address. Please try again.")
#     except Exception as e:
#         update.message.reply_text("An error occurred. Please try again later.")

# def get_pharmacy_addresses() -> list[str]:
#     conn = sqlite3.connect("farmacie.db")
#     cursor = conn.cursor()

#     # Assuming you have a table named 'pharmacies' with an 'address' column
#     cursor.execute("SELECT Indirizzo FROM farmacie")
#     rows = cursor.fetchall()

#     # Extract the addresses from the rows
#     pharmacy_addresses = [row[0] for row in rows]

#     conn.close()

#     return pharmacy_addresses



# if __name__ == '__main__':
#     main()

# import sqlite3
# from geopy.distance import geodesic
# from geopy.geocoders import Nominatim
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# TOKEN = '5643203403:AAEjSi-VlOLREODuq60Tm19wyjPmhHBpvjs'

# database_name = "farmacie.db"

# def start(update, context):
#     context.bot.send_message(chat_id=update.effective_chat.id,
#                              text="I will find the closest pharmacy to your location.")

# def get_user_location(update, context):
#     user_id = update.effective_user.id

    
#     user = context.bot.get_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
#     user_location = user.location

#     latitude = user_location.latitude
#     longitude = user_location.longitude

#     return latitude, longitude

# def find_closest_pharmacy(latitude, longitude):
#     user_coordinates = (latitude, longitude)
#     geolocator = Nominatim(user_agent="my_bot")

#     closest_pharmacy = None
#     closest_address = None
#     closest_distance = float('inf')

    
#     conn = sqlite3.connect(database_name)
#     cursor = conn.cursor()

    
#     cursor.execute("SELECT Indirizzo FROM sqlite_master")
#     tables = cursor.fetchall()

#     for table in tables:
#         table_name = table[0]

        
#         cursor.execute(f"SELECT Nome, Indirizzo FROM {table_name}")
#         rows = cursor.fetchall()

#         for row in rows:
#             pharmacy_name = row[0]
#             pharmacy_address = row[1]
#             location = geolocator.geocode(pharmacy_address)

#             if location is not None:
#                 pharmacy_coordinates = (location.latitude, location.longitude)
#                 distance = geodesic(user_coordinates, pharmacy_coordinates).meters

#                 if distance < closest_distance:
#                     closest_pharmacy = pharmacy_name
#                     closest_address = pharmacy_address
#                     closest_distance = distance

#     # Close the database connection
#     cursor.close()
#     conn.close()

#     if closest_pharmacy:
#         return f"The closest pharmacy is:\n\nName: {closest_pharmacy}\nAddress: {closest_address}"
#     else:
#         return "No pharmacy found."

# def handle_location(update, context):
#     latitude, longitude = get_user_location(update, context)

#     closest_pharmacy_message = find_closest_pharmacy(latitude, longitude)
#     context.bot.send_message(chat_id=update.effective_chat.id, text=closest_pharmacy_message)

# def main():
#     updater = Updater(token=TOKEN, use_context=True)
#     dispatcher = updater.dispatcher

#     start_handler = CommandHandler('start', start)
#     location_handler = MessageHandler(Filters.location, handle_location)

#     dispatcher.add_handler(start_handler)
#     dispatcher.add_handler(location_handler)

#     updater.start_polling()
#     updater.idle()

# if __name__ == '__main__':
#     main()


##CODICE DI DAVIDE
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# from geopy.geocoders import *
# from geopy.distance import *
# from geopy.geocoders import Nominatim
# import re


# messaggio = ""

# # Funzione per gestire il comando /geolocalizzazione
# def geolocalizzazione(update, context):
#     context.chat_data['aspettando_indirizzo'] = True
#     update.message.reply_text('Scrivi l\'indirizzo nel formato "Nome via, numero civico, città, provincia"')

# def geolocalizza(update, context, indirizzo):
#     geolocator = Nominatim(user_agent="my_app")
#     # First address
#     address1 = "Via Marsala, 18, Villafranca di Verona, VR, Italy"
#     location1 = geolocator.geocode(address1)

#     # Second address
#     location2 = geolocator.geocode(indirizzo)
    
#     if location1 and location2:
#         point1 = (location1.latitude, location1.longitude)
#         point2 = (location2.latitude, location2.longitude)
    
#         distance = geodesic(point1, point2).km
#         context.bot.send_message(chat_id=update.message.chat_id, text=f"La distanza da te e la farmacia {address1} è di {distance:.2f} kilometri")
#     else:
#         context.bot.send_message(chat_id=update.message.chat_id, text=f"Non è stato possibile trovare la tua via, sicuro di aver inserito la via corretta?")


# def handle_message(update, context):
    
#     message = update.message

#     print(message)

#     if 'aspettando_indirizzo' in context.chat_data and context.chat_data['aspettando_indirizzo']:
#         indirizzo = update.message.text
#         geolocalizza(update, context, indirizzo)
#         update.message.reply_text(f'Hai inserito l\'indirizzo: {indirizzo}')
#         del context.chat_data['aspettando_indirizzo']

#     if message.text.lower() == "こんにちわ":
#         context.bot.send_message(chat_id=message.chat_id, text='はじめましてヴィンチェンゾです')

#     if message.text.lower().startswith('/chat '):
#         global messaggio 
#         messaggio = message.text.lower()
#         messaggio = re.sub(r'/chat ', '', messaggio)
#         context.bot.send_message(chat_id=update.message.chat_id, text=f'{update.message.from_user.first_name}:\n{messaggio}')

# def start(update, context):
#     user_name = update.message.from_user.first_name
    
#     update.message.reply_text(f'Ciao {user_name}! Sono PharmaBot, ho la funzione di aiutarti a scegliere la farmacia ideale e più conveniente per te!')

# def chat(update, context):
#     global messaggio

#     if messaggio is not None:
#         penUltimoMess = messaggio

#     messaggio = update.message.text

#     print(f"messaggio {messaggio.lower()} e penUltimoMess {penUltimoMess}")
#     context.bot.send_message(chat_id=update.message.chat_id, text=f'{update.message.from_user.first_name}:\n{messaggio}')

# def main():
#     updater = Updater('5643203403:AAEjSi-VlOLREODuq60Tm19wyjPmhHBpvjs')

#     dispatcher = updater.dispatcher

#     dispatcher.add_handler(CommandHandler('start', start))

#     dispatcher.add_handler(CommandHandler('geolocalizzazione', geolocalizzazione))

#     dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

#     updater.start_polling()

#     updater.idle()

# if __name__ == '__main__':
#     main()

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode, ReplyKeyboardMarkup, KeyboardButton
import sqlite3
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import geopy


# Telegram bot token
TOKEN = '5643203403:AAEjSi-VlOLREODuq60Tm19wyjPmhHBpvjs'

def start(update, context):
    user = update.effective_user
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Hello, {user.first_name}! I will retrieve your location.")

    # Request the user's location
    request_location_button = KeyboardButton(text="Share Location", request_location=True)
    reply_markup = ReplyKeyboardMarkup([[request_location_button]], resize_keyboard=True, one_time_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Please click the 'Share Location' button to provide your location.",
                             reply_markup=reply_markup)


def handle_location(update, context):
    try:
        #user = update.message.from_user
        address = update.message.location.address

        geolocator = Nominatim(user_agent="pharmabot")
        location = None
        retries = 0
        while location is None and retries < 3:
            try:
                location = geolocator.geocode(address)
            except geopy.exc.GeocoderTimedOut:
                retries += 1

        if location is not None:
            user_location = (location.latitude, location.longitude)
            pharmacy_location = nearest_pharmacy(user_location)
            reply_text = f"Nearest pharmacy: {pharmacy_location['NomeFarmacia']}\nAddress: {pharmacy_location['Indirizzo']}"
        else:
            reply_text = "Sorry, I couldn't find your location."

        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)
    except Exception as e:
        print(e)





def nearest_pharmacy(update, context):
    user = update.effective_user
    location = update.effective_message.location

    latitude = location.latitude
    longitude = location.longitude

    # Connect to the database
    conn = sqlite3.connect("farmacie.db")
    cursor = conn.cursor()

    # Get a list of table names in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = [name[0] for name in cursor.fetchall()]

    # Find the nearest address in each table based on the user's position
    results = []
    for table_name in table_names:
        cursor.execute("SELECT Indirizzo FROM {}".format(table_name))
        addresses = [address[0] for address in cursor.fetchall()]
        print(addresses)
        distances = []
        for address in addresses:
            geolocator = Nominatim(user_agent="my_app")
            location = geolocator.geocode(address)
            if location:
                point = (location.latitude, location.longitude)
                distance = geodesic((latitude, longitude), point).km
                distances.append(distance)

        if distances:
            min_distance = min(distances)
            min_index = distances.index(min_distance)
            nearest_address = addresses[min_index]

            results.append((nearest_address, table_name))

    if results:
        # Sort the results based on the shortest distance
        results.sort(key=lambda x: geodesic((latitude, longitude), geolocator.geocode(x[0]).point).km)

        # Extract the nearest address and pharmacy name
        nearest_address, table_name = results[0]

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Nearest address: {nearest_address}\nTable Name: {table_name}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="No nearest address found in the database.")

    # Close the database connection
    conn.close()

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Thank you, {user.first_name}! I have retrieved your location:\n\nLatitude: {latitude}\nLongitude: {longitude}")




def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    nearest_pharmacy_handler = CommandHandler('nearestpharmacy', nearest_pharmacy) #**** In questa funzione farai un ciclo for con la posizione dell'utente che contiene lat. e long., le confronti con tutti gli indirizzi finchè nono trovi il valore minimo (trova coordinate degli addresses)
    #guarda la chat telegram con Daniele per vedere la funzione per calcolare la distanza tra punti che incorporerai nel ciclo for (penso di sostituire quest'ultima funzione alla handle_location(), che verrà richiamata nella nearest_pharmacy())
    dispatcher.add_handler(nearest_pharmacy_handler) #crea una copia del file
    
    
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    location_handler = MessageHandler(Filters.location, handle_location)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(location_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()






