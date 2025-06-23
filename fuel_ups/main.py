from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim


def get_coordinates(address):
    """
    Gets the latitude and longitude of an address using Nominatim.

    Args:
        address (str): The address string.

    Returns:
        tuple: (latitude, longitude) if successful, None otherwise.
    """
    geolocator = Nominatim(
        user_agent="my-geocoding-app"
    )  # Replace "my-geocoding-app" with a unique name
    try:
        location = geolocator.geocode(address, timeout=10)  # Set a timeout
        if location:
            return (location.latitude, location.longitude)
        else:
            print(f"Could not find coordinates for: {address}")
            return None
    except GeocoderTimedOut:
        print(f"Geocoding service timed out for: {address}")
        return None
    except GeocoderServiceError as e:
        print(f"Geocoding service error for {address}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred for {address}: {e}")
        return None


# --- Examples ---
print("--- Geocoding Examples ---")
address1 = "PETRO STOPPING CENTER #306"
coords1 = get_coordinates(address1)
if coords1:
    print(
        f"Coordinates for '{address1}': Latitude={coords1[0]}, Longitude={coords1[1]}"
    )
print("-" * 30)

# Example 1: A well-known address
# address1 = "Eiffel Tower, Paris"
# coords1 = get_coordinates(address1)
# if coords1:
#     print(
#         f"Coordinates for '{address1}': Latitude={coords1[0]}, Longitude={coords1[1]}"
#     )
# print("-" * 30)

# # Example 2: A different address
# address2 = "Times Square, New York"
# coords2 = get_coordinates(address2)
# if coords2:
#     print(
#         f"Coordinates for '{address2}': Latitude={coords2[0]}, Longitude={coords2[1]}"
#     )
# print("-" * 30)

# # Example 3: A more specific address (e.g., in Abuja, Nigeria)
# # Remember the current location is Abuja, Federal Capital Territory, Nigeria.
# address3 = "Wuse 2, Abuja, Nigeria"
# coords3 = get_coordinates(address3)
# if coords3:
#     print(
#         f"Coordinates for '{address3}': Latitude={coords3[0]}, Longitude={coords3[1]}"
#     )
# print("-" * 30)

# # Example 4: An address that might not be found or is ambiguous
# address4 = "Nonexistent Street 123, Nowhere"
# coords4 = get_coordinates(address4)
# if coords4:  # This block likely won't execute as it should return None
#     print(
#         f"Coordinates for '{address4}': Latitude={coords4[0]}, Longitude={coords4[1]}"
#     )
# print("-" * 30)
