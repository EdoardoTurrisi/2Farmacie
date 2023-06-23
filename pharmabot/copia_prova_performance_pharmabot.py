from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode, ReplyKeyboardMarkup, KeyboardButton
import sqlite3
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


# Telegram bot token
TOKEN = '5643203403:AAEjSi-VlOLREODuq60Tm19wyjPmhHBpvjs'

# Cache for storing geocoded addresses
geocode_cache = {}

def start(update, context):
    user = update.effective_user
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello, {user.first_name}! I will retrieve your location.")

    # Request the user's location
    request_location_button = KeyboardButton(text="Share Location", request_location=True)
    reply_markup = ReplyKeyboardMarkup([[request_location_button]], resize_keyboard=True, one_time_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please click the 'Share Location' button to provide your location.", reply_markup=reply_markup)

    # Set the flag to indicate that the program is waiting for the user's location
    context.user_data['waiting_for_location'] = True

    # Remove the 'waiting_for_location' flag after 5 seconds
    job_queue = context.job_queue
    job_queue.run_once(remove_waiting_flag, 5, context=update.effective_chat.id)

def remove_waiting_flag(context):
    chat_id = context.job.context
    context.dispatcher.user_data.pop('waiting_for_location', None)


def geocode_address(geolocator, address):
    if address in geocode_cache:
        return geocode_cache[address]
    else:
        location = geolocator.geocode(address)
        if location:
            geocode_cache[address] = location
            return location
        else:
            return None


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
            location = geocode_address(geolocator, address)
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
        results.sort(key=lambda x: geodesic((latitude, longitude), geocode_address(geolocator, x[0]).point).km)

        # Extract the nearest address and pharmacy name
        nearest_address, table_name = results[0]

        reply_text = f"Nearest pharmacy: {table_name}\nAddress: {nearest_address}"
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)

    # Close the database connection
    conn.close()

def nearest_pharmacy(update, context):
    user = update.effective_user

    # Check if the user provided a location
    if update.effective_message.location is None:
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
    geolocator = Nominatim(user_agent="pharmabot")
    for table_name in table_names:
        if not table_name:  # Skip empty table names
            continue

        cursor.execute("SELECT Indirizzo FROM {}".format(table_name))
        addresses = [address[0] for address in cursor.execute("SELECT Indirizzo FROM {}".format(table_name))]
        distances = []
        for address in addresses:
            location = geocode_address(geolocator, address)
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
        results.sort(key=lambda x: geodesic((latitude, longitude), geocode_address(geolocator, x[0]).point).km)

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

    start_handler = CommandHandler('start', start)
    location_handler = MessageHandler(Filters.location, handle_location)
    nearest_pharmacy_handler = CommandHandler('nearestpharmacy', nearest_pharmacy)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(location_handler)
    dispatcher.add_handler(nearest_pharmacy_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()