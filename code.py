#APRIL 1 2022 
#Jorge Enrique Gamboa Fuentes
#Subway schedule board - single direction
#Data from: Boston - MBTA
# .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - 

import time
import microcontroller
from board import NEOPIXEL
import displayio
import adafruit_display_text.label
import adafruit_display_text.scrolling_label
from adafruit_datetime import datetime
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.network import Network
import json
import gc

#CONFIGURABLE PARAMETERS
#-*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*-
BOARD_TITLE = 'Boston College'
STOP_ID = 'place-kencl'
DIRECTION_ID = '0'
ROUTE = 'Green-B'
BACKGROUND_IMAGE = 'TGreen-dashboard.bmp'
PAGE_LIMIT = '3'
DATA_SOURCE = 'https://api-v3.mbta.com/predictions?filter%5Bstop%5D='+STOP_ID+'&filter%5Bdirection_id%5D='+DIRECTION_ID+'&filter%5Broute%5D='+ROUTE+'&page%5Blimit%5D='+PAGE_LIMIT+'&sort=departure_time'
UPDATE_DELAY = 20
SYNC_TIME_DELAY = 50
MINIMUM_MINUTES_DISPLAY = 9
ERROR_RESET_THRESHOLD = 3
#-*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*-

def get_arrival_in_minutes_from_now(now, date_str):
    train_date = datetime.fromisoformat(date_str).replace(tzinfo=None) # Remove tzinfo to be able to diff dates
    return round((train_date-now).total_seconds()/60.0)

def get_arrival_times():
    now = datetime.now()
    print(now)
    print("Data source: "+DATA_SOURCE)
    stop_trains =  network.fetch_data(DATA_SOURCE)
    res = json.loads(stop_trains)
    # print(res)
    try:
        train1 = res["data"][0]["attributes"]["departure_time"]
        train1_min = get_arrival_in_minutes_from_now(now, train1) - 1
    except:
        train1_min=-999
    try:
        train2 = res["data"][1]["attributes"]["departure_time"]
        train2_min = get_arrival_in_minutes_from_now(now, train2) - 1
    except:
        train2_min=-888
    try:
        train3 = res["data"][2]["attributes"]["departure_time"]
        train3_min = get_arrival_in_minutes_from_now(now, train3) - 1 
    except:
        train3_min=-777

    return train1_min,train2_min,train3_min

def text_formating(trainMinutes):
    textFormated = ""
    if(trainMinutes<=0 & trainMinutes > -100):
        textFormated = "Now"
    elif(trainMinutes<10):
        textFormated = "%s  min" % (trainMinutes)
    else: 
        textFormated = "%s min" % (trainMinutes)
    
    if(trainMinutes==-777):
        textFormated = "-----"
    elif(trainMinutes==-888):
        textFormated = "-----"
    elif(trainMinutes==-999):
        textFormated = "-----"

    return textFormated


def text_formating2(trainMinutes):
    textFormated = ""
    if(trainMinutes<=0 & trainMinutes > -100):
        textFormated = "Now"
    elif(trainMinutes<10):
        textFormated = str(trainMinutes) + "  min"
    else: 
        textFormated = str(trainMinutes) + " min"

    if(trainMinutes==-777):
        textFormated = "-----"
    elif(trainMinutes==-888):
        textFormated = "-----"
    elif(trainMinutes==-999):
        textFormated = "-----"

    return textFormated

def update_text(t1, t2, t3):

    text_lines[2].text = text_formating2(t1)
    text_lines[3].text = text_formating2(t2)
    text_lines[4].text = text_formating2(t3)
    
    # text_lines[2].text = str(t1)
    # text_lines[3].text = "10 min"
    # text_lines[4].text = "18 min"
    gc.collect()


# --- Display setup ---
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=NEOPIXEL, debug=False)

# --- Drawing setup ---
group = displayio.Group()
bitmap = displayio.OnDiskBitmap(open(BACKGROUND_IMAGE, 'rb'))
colors = [0x444444, 0xDD8000]  # [dim white, gold]



font = bitmap_font.load_font("fonts/6x10.bdf")

title = adafruit_display_text.label.Label(font, color=colors[0], x=20, y=3, text=BOARD_TITLE)
# title = adafruit_display_text.scrolling_label.ScrollingLabel(font, max_characters=7, color=colors[0], x=20, y=3, text=BOARD_TITLE)

text_lines = [
    displayio.TileGrid(bitmap, pixel_shader=getattr(bitmap, 'pixel_shader', displayio.ColorConverter())),
    title,
    adafruit_display_text.label.Label(font, color=colors[1], x=26, y=11, text="- min"),
    adafruit_display_text.label.Label(font, color=colors[1], x=26, y=20, text="- min"),
    adafruit_display_text.label.Label(font, color=colors[1], x=26, y=28, text="- min"),
]
for x in text_lines:
    group.append(x)
display.root_group = group

error_counter = 0
last_time_sync = time.monotonic() - SYNC_TIME_DELAY - 1
last_fetch = time.monotonic() - UPDATE_DELAY - 1

while True:
    try:
        if time.monotonic() > last_time_sync + SYNC_TIME_DELAY:
            # Sync clock to minimize time drift
            network.get_local_time()
            last_time_sync = time.monotonic()
        #print("-*--> ENRIQUE HERE")
        #print(get_arrival_times())
        if time.monotonic() > last_fetch + UPDATE_DELAY:
            t1, t2, t3 = get_arrival_times()
            print(t1, t2, t3)
            last_fetch = time.monotonic()
            update_text(t1, t2, t3)
            # update_text(*arrivals)
        # title.update()
    except (ValueError, RuntimeError) as e:
        print("Some error occured, retrying! -", e)
        error_counter = error_counter + 1
        if error_counter > ERROR_RESET_THRESHOLD:
            microcontroller.reset()

    # time.sleep(UPDATE_DELAY)