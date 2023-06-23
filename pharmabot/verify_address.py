from geopy.geocoders import Nominatim

def is_valid_address(address):
    geolocator = Nominatim(user_agent="address_verification")
    try:
        location = geolocator.geocode(address)
        if location is not None:
            return True
    except Exception as e:
        print("Error:", e)
    return False

address = "Via Verona, 14, 37012 Bussolengo VR"
is_valid = is_valid_address(address)
if is_valid:
    print("Address is valid")
else:
    print("Address is not valid")
