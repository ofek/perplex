import time

# Mine
DEFAULT_TIME_ZONE = 'America/New_York'

# Windows names taken from:
# https://docs.microsoft.com/en-us/windows-hardware/manufacture/desktop/default-time-zones
# https://support.microsoft.com/en-us/help/973627/microsoft-time-zone-index-values
#
# You can easily mock unix time zones to see its names.
# Use https://en.wikipedia.org/wiki/List_of_tz_database_time_zones like this:
# python -c "import os, time; os.environ['TZ'] = 'Europe/London'; time.tzset(); print(time.tzname)"
#
# Storage regions: https://cloud.google.com/storage/docs/locations#available_locations
#
# Zones within the same region may have different resources available. See:
# https://cloud.google.com/compute/docs/regions-zones/#available
#
# Try to select zones with local SSDs and if possible GPUs.
DEFAULT_LOCATIONS = {
    # Hollywood
    ('PST', 'PDT'): ('us-west2-c', 'us-west2'),
    ('Pacific Standard Time', 'Pacific Daylight Time'): ('us-west2-c', 'us-west2'),
    # Yellowstone Supervolcano
    ('MST', 'MDT'): ('us-central1-c', 'us-central1'),
    ('Mountain Standard Time', 'Mountain Daylight Time'): ('us-central1-c', 'us-central1'),
    # The Wizard of Oz
    ('CST', 'CDT'): ('us-central1-c', 'us-central1'),
    ('Central Standard Time', 'Central Daylight Time'): ('us-central1-c', 'us-central1'),
    # Gotham
    ('EST', 'EDT'): ('us-east4-b', 'us-east4'),
    ('Eastern Standard Time', 'Eastern Daylight Time'): ('us-east4-b', 'us-east4'),
    # Brazil - WSL gave me ('-03', '-02') but I doubt its commitment to Sparkle Motion
    ('-03', '-02'): ('southamerica-east1-b', 'southamerica-east1'),
    ('E. South America Standard Time', 'E. South America Daylight Time'): (
        'southamerica-east1-b',
        'southamerica-east1',
    ),
    # Big Ben
    ('GMT', 'BST'): ('europe-west2-b', 'europe-west2'),
    ('GMT Standard Time', 'GMT Daylight Time'): ('europe-west2-b', 'europe-west2'),
    # "Europe"
    ('CET', 'CEST'): ('europe-west1-d', 'europe-west1'),
    ('Romance Standard Time', 'Romance Daylight Time'): ('europe-west1-d', 'europe-west1'),
    # "Eastern Europe" - only Windows users in the south will properly use the closest data center
    ('EET', 'EEST'): ('europe-north1-b', 'europe-north1'),
    ('FLE Standard Time', 'FLE Daylight Time'): ('europe-north1-b', 'europe-north1'),
    ('GTB Standard Time', 'GTB Daylight Time'): ('europe-west1-d', 'europe-west1'),
    # Marxism & great genes
    ('MSK', 'MSK'): ('europe-north1-b', 'europe-north1'),
    ('Russian Standard Time', 'Russian Daylight Time'): ('europe-north1-b', 'europe-north1'),
    # Israel & India - like the North Pole & Antarctica, but a bit closer
    ('IST', 'IDT'): ('asia-south1-b', 'asia-south1'),
    ('India Standard Time', 'India Daylight Time'): ('asia-south1-b', 'asia-south1'),
    ('Israel Standard Time', 'Israel Daylight Time'): ('asia-south1-b', 'asia-south1'),
    # Hong Kong
    ('HKT', 'HKT'): ('asia-east2-b', 'asia-east2'),
    # China?
    ('CST', 'CST'): ('asia-east1-b', 'asia-east1'),
    ('China Standard Time', 'China Daylight Time'): ('asia-east1-b', 'asia-east1'),
    ('Taipei Standard Time', 'Taipei Daylight Time'): ('asia-east1-b', 'asia-east1'),
    # Singapore - WSL gave me ('+08', '+08') but I also lack faith in that
    ('+08', '+08'): ('asia-southeast1-b', 'asia-southeast1'),
    ('Singapore Standard Time', 'Singapore Daylight Time'): ('asia-southeast1-b', 'asia-southeast1'),
    # Kawaii over 9000
    ('JST', 'JST'): ('asia-northeast1-b', 'asia-northeast1'),
    ('Tokyo Standard Time', 'Tokyo Daylight Time'): ('asia-northeast1-b', 'asia-northeast1'),
    # Convicts & Crocodiles
    ('ACST', 'ACDT'): ('australia-southeast1-b', 'australia-southeast1'),
    ('AEST', 'AEDT'): ('australia-southeast1-b', 'australia-southeast1'),
    ('AEST', 'AEST'): ('australia-southeast1-b', 'australia-southeast1'),
    ('AWST', 'AWST'): ('australia-southeast1-b', 'australia-southeast1'),
    ('AUS Eastern Standard Time', 'AUS Eastern Daylight Time'): ('australia-southeast1-b', 'australia-southeast1'),
    ('Cen. Australia Standard Time', 'Cen. Australia Daylight Time'): (
        'australia-southeast1-b',
        'australia-southeast1',
    ),
    ('E. Australia Standard Time', 'E. Australia Daylight Time'): ('australia-southeast1-b', 'australia-southeast1'),
    ('W. Australia Standard Time', 'W. Australia Daylight Time'): ('australia-southeast1-b', 'australia-southeast1'),
    # The Shire
    ('NZST', 'NZDT'): ('australia-southeast1-b', 'australia-southeast1'),
    ('New Zealand Standard Time', 'New Zealand Daylight Time'): ('australia-southeast1-b', 'australia-southeast1'),
}


def get_detected_time_zones():
    try:
        return time.tzname
    except AttributeError:
        pass


def get_default_locations():
    try:
        return DEFAULT_LOCATIONS[get_detected_time_zones()]
    except KeyError:
        return None, None


def get_time_zone():
    from pytz.exceptions import UnknownTimeZoneError
    from tzlocal import get_localzone

    try:
        timezone = get_localzone().zone
    except UnknownTimeZoneError:
        pass
    else:
        # Return only if the call gave us something valid. See:
        # https://github.com/regebro/tzlocal/issues/44
        if timezone and timezone != 'local':
            return timezone

    return DEFAULT_TIME_ZONE
