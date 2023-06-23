from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode, ReplyKeyboardMarkup, KeyboardButton
import sqlite3
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Telegram bot token
with open("token.txt", "r") as f:
    TOKEN = f.read()

def start(update, context):
    user = update.effective_user
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ciao {user.first_name}, benvenuto su Pharmabot! Con questo bot potrai ottenere informazioni riguardo alle farmacie nella tua zona e a quella più vicina a te. \nSe trovi alcuni problemi con il bot non esitare a scriverci all'email edoardogiuseppeturrisi@gmail.com")

    # Request the user's location
    request_location_button = KeyboardButton(text="Condividi la posizione", request_location=True)
    reply_markup = ReplyKeyboardMarkup([[request_location_button]], resize_keyboard=True, one_time_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Per favore condividi la tua posizione prima di eseguire il comando della geolocalizzazione.", reply_markup=reply_markup)

def handle_location(update, context):
    
    
    user = update.message.from_user
    location = update.message.location

    latitude = location.latitude
    longitude = location.longitude

    geolocator = Nominatim(user_agent="pharmabot")
    address = geolocator.reverse((latitude, longitude)).address

    # Connect to the database
    conn = sqlite3.connect("farmacie.db")
    cursor = conn.cursor()

    # Get a list of table names in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = [name[0] for name in cursor.fetchall()]

    # Find the nearest address in each table based on the user's position
    results = []
    for table_name in table_names:
        if not table_name:  # Skip empty table names
            continue

        cursor.execute("SELECT Indirizzo FROM {}".format(table_name))
        addresses = [address[0] for address in cursor.execute("SELECT Indirizzo FROM {}".format(table_name))]
        distances = []
        for address in addresses:
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

        reply_text = f"\nComune: {table_name}\nIndirizzo: {nearest_address}"
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)

    # Close the database connection
    conn.close()

def nearest_pharmacy(update, context):
    user = update.effective_user

    # Check if the user provided a location
    if update.effective_message.location is None:
        #context.bot.send_message(chat_id=update.effective_chat.id, text="No location provided.")
        return

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
        if not table_name:  # Skip empty table names
            continue

        cursor.execute("SELECT Indirizzo FROM {}".format(table_name))
        addresses = [address[0] for address in cursor.execute("SELECT Indirizzo FROM {}".format(table_name))]
        distances = []
        for address in addresses:
            geolocator = Nominatim(user_agent="pharmabot")
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
                                 text=f"Indirizzo farmacia: {nearest_address}\nTable Name: {table_name}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Nessun indirizzo è stato trovato")

    # Close the database connection
    conn.close()


    context.bot.send_message(chat_id=update.effective_chat.id,
                              text=f"Grazie, {user.first_name}! Ho ottenuto la tua posizione:\n\nLatitude: {latitude}\nLongitude: {longitude}")

def elenco_farmacie(update, context):
    user = update.effective_user
    acceptable_names = ['bussolengo', 'castelnuovo', 'mozzecane', 'pastrengo', 'pescantina', 'sommacampagna', 'sona', 'valeggio', 'villafranca', 'vigasio']

    # Send the list of acceptable names to the user
    context.bot.send_message(chat_id=update.effective_chat.id, text="Elenca le farmacie disponibili usando uno dei seguenti nomi:")
    context.bot.send_message(chat_id=update.effective_chat.id, text=", ".join(acceptable_names))

    # Set the flag to indicate that the program is waiting for the user's input
    context.user_data['waiting_for_input'] = True

def process_elenco_farmacie(update, context):
    user_input = update.message.text.lower()

    # Check if the user provided a valid input
    if 'waiting_for_input' not in context.user_data or not context.user_data['waiting_for_input']:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Il servizio di localizzazione GPS sta subendo dei problemi; attendere...")
        return

    acceptable_names = ['bussolengo', 'castelnuovo', 'mozzecane', 'pastrengo', 'pescantina', 'sommacampagna', 'sona', 'valeggio', 'villafranca', 'vigasio']

    if user_input not in acceptable_names:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Nome non valido. Riprova.")
        return

    # Connect to the database
    conn = sqlite3.connect("farmacie.db")
    cursor = conn.cursor()

    # Retrieve the names and addresses of the pharmacies in the specified table
    cursor.execute(f"SELECT NomeFarmacia, Indirizzo FROM {user_input}")
    results = cursor.fetchall()

    if results:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Elenca farmacie:")
        for name, address in results:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Nome Farmacia: {name}\nIndirizzo: {address}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Nessuna farmacia trovata.")

    # Close the database connection
    conn.close()

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    location_handler = MessageHandler(Filters.location, handle_location)
    nearest_pharmacy_handler = CommandHandler('geolocalizzazione', nearest_pharmacy)
    elenco_farmacie_handler = CommandHandler('elencofarmacie', elenco_farmacie)
    process_elenco_farmacie_handler = MessageHandler(Filters.text, process_elenco_farmacie)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(location_handler)
    dispatcher.add_handler(nearest_pharmacy_handler)
    dispatcher.add_handler(elenco_farmacie_handler)
    dispatcher.add_handler(process_elenco_farmacie_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
