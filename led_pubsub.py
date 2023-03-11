import board
import neopixel
import requests
import re
import asyncio
import local_auth
import sys
from time import sleep
from twitchAPI.twitch import Twitch
from twitchAPI.pubsub import PubSub
from twitchAPI.types import AuthScope
from twitchAPI.types import CustomRewardRedemptionStatus
from pprint import pprint
from uuid import UUID
from websocket import create_connection

default_redeem = 'Multi-Colored'

"""Converts a HEX code into RGB or HSL.
Args:
    hx (str): Takes both short as well as long HEX codes.
    hsl (bool): Converts the given HEX code into HSL value if True.
Return:
    Tuple of length 3 consisting of either int or float values.
Raise:
    ValueError: If given value is not a valid HEX code."""
def hex_to_rgb(hx, hsl=False):
    if re.compile(r'#[a-fA-F0-9]{3}(?:[a-fA-F0-9]{3})?$').match(hx):
        div = 255.0 if hsl else 0
        if len(hx) <= 4:
            return tuple(int(hx[i]*2, 16) / div if div else
                         int(hx[i]*2, 16) for i in (1, 3, 2))
        return tuple(int(hx[i:i+2], 16) / div if div else
                     int(hx[i:i+2], 16) for i in (1, 5, 3))
    print(f'"{hx}" is not a valid HEX code.')

#Channel Points Redeem via Twitch API
def callback_points_redeem(uuid: UUID, data: dict) -> None:
    user = data['data']['redemption']['user']['display_name']
    redeem = data['data']['redemption']['reward']['title']
    redemptionID = data['data']['redemption']['id']
    rewardID = data['data']['redemption']['reward']['id']
    status = data['data']['redemption']['status']
    if 'user_input' in data['data']['redemption']:
      user_input = data['data']['redemption']['user_input']
    else:
      user_input = False
    redeem_color(redeem)
    print('\n' + user + ' redeemed ' + redeem)
    #To be implemented later, need to recreate rewards using client id
    #twitch.update_redemption_status(user_id, rewardID, redemptionID, CustomRewardRedemptionStatus.FULFILLED)


#Subs via Twitch API
def callback_subs(uuid: UUID, data: dict) -> None:
    global default_redeem
    print(data)
    flash_alert(10, 255, 0, 0)
    redeem_color(default_redeem)

#Bits via Twitch API
def callback_bits(uuid: UUID, data: dict) -> None:
    global default_redeem
    bits = data['data']['bits_used'] #Collect how many bits were used
    user = data['data']['user_name'] #Collect name for Printout
    if bits < 20:
      flash_alert(1, 80, 5, 40) #bits under 20 get 1 second of dark purple
    elif bits <= 999:
      t = int(bits / 20)
      if t > 20:
        t = 20
      flash_alert(t, 255, 0, 125) #bits 20-999 get divided by 20 with a maximum of 20 and run with purple
    elif bits <= 4999:
      t = int(bits / 100) 
      if t > 30:
        t = 30
      flash_alert(t, 10, 125, 40)#bits 1000-4999 get divided by 100 with a maximum of 30 and run with green
    elif bits <= 9999:
      flash_alert(30, 30, 30, 255)#bits 5000-9999 get 30 of blue
    elif bits <= 99999:
      flash_alert(30, 255, 0, 0)#bits 10000-99999 get 30 of red
    else:
      flash_alert(30, 104, 45, 0)#bits more than 100000 get 30 of orange
    print(user + ' cheered with ' + bits + ' bits!')
    flash_alert(t, 255, 0, 125)
    redeem_color(default_redeem)

#Channel Points Redemption Switch
def redeem_color(redeem, u = False):
    global default_redeem
    if redeem == 'wee-woo (10 seconds)':
      wee_woo(2)
      redeem_color(default_redeem)
    elif redeem == 'red':
      set_all(70, 0, 0)
      block_set(left_shelf, 255, 0, 0)
      block_set(right_shelf, 255, 0, 0)
      show_all()
      sleep(1)      
      default_redeem = 'red'
    elif redeem == 'green':
      set_all(0, 100, 0)
      block_set(left_shelf, 0, 255, 0)
      block_set(right_shelf, 0, 255, 0)
      show_all()
      sleep(1)
      default_redeem = 'green'
    elif redeem == 'blue':
      set_all(10, 10, 70)
      block_set(left_shelf, 0, 0, 255)
      block_set(right_shelf, 0, 0, 255)
      block_set(top_edge, 0, 0, 100)
      show_all()
      sleep(1)
      default_redeem = 'blue'
    elif redeem == 'purple':
      set_all(70, 0, 160)
      block_set(left_shelf, 145, 0, 255)
      block_set(right_shelf, 145, 0, 255)
      show_all()
      sleep(1)
      default_redeem = 'purple'
    elif redeem == 'aqua':
      set_all(10, 100, 100)
      block_set(left_shelf, 40, 125, 125)
      block_set(right_shelf, 40, 125, 125)
      show_all()
      sleep(1)
      default_redeem = 'aqua'
    elif redeem == 'orange':
      set_all(104, 45, 0)
      block_set(left_shelf, 255, 100, 0)
      block_set(right_shelf, 255, 100, 0)
      show_all()
      sleep(1)
      default_redeem = 'orange'
    elif redeem == 'Sienna':
      set_all(111, 31, 0)
      show_all()
      sleep(1)
      default_redeem = 'Sienna'
    elif redeem == 'Hot Pink':
      set_all(128, 0, 40)
      show_all()
      sleep(1)
      default_redeem = 'Hot Pink'
    elif redeem == 'Multi-Colored':
      multi_color()
      sleep(1)
      default_redeem = 'Multi-Colored'
    elif redeem == 'Strobe (5 seconds)':
      strobe(40)
      redeem_color(default_redeem)
    elif redeem == 'Custom Color':
      rgb_val = hex_to_rgb(u)
      set_all(rgb_val)
      print(rgb_val)
      show_all()
      default_redeem = 'Multi-Colored'
    elif redeem == 'Off':
      set_all(0,0,0)
      show_all()
      default_redeem = 'Off'
    elif redeem == 'Workbench Only (white)':
      set_all(0,0,0)
      block_set(workbench_top, 255, 255, 255)
      show_all()
    elif redeem == 'All White Everything':
      set_all(255, 255, 255)
      show_all()
    elif redeem == 'Rainbow Puke (10 seconds)':
      rainbow_cycle(400)
      redeem_color(default_redeem)
    elif redeem == 'chillin':
      chillin()
      default_redeem = 'chillin'
    else:
      print(redeem + ' isn\'t a function')

#authorization
my_app_key = local_auth.twitch_key
my_app_secret = local_auth.twitch_secret
my_user_auth_token = local_auth.twitch_user_token
lumia_token = local_auth.lumia_token

#Twitch Auth
twitch = Twitch(my_app_key, my_app_secret)
twitch.auto_refresh_auth = False
twitch.authenticate_app([])
target_scope = [AuthScope.BITS_READ, AuthScope.CHANNEL_READ_REDEMPTIONS, AuthScope.CHANNEL_READ_SUBSCRIPTIONS, AuthScope.CHANNEL_MANAGE_REDEMPTIONS]
twitch.set_user_authentication(my_user_auth_token, target_scope)
user_id = twitch.get_users(logins=['NRG_'])['data'][0]['id']
pubsub = PubSub(twitch)
pubsub.start() #Start PubSub Web Socket
points_redeem = pubsub.listen_channel_points(user_id, callback_points_redeem)
bit_alert = pubsub.listen_bits(user_id, callback_bits)
sub_alert = pubsub.listen_channel_subscriptions(user_id, callback_subs)

'''
#LumiaStream WebSocket Listener
lumia_url = "ws://192.168.0.136:39231/api?token=" + lumia_token
print(lumia_url)
lumia_ws = create_connection(lumia_url)
'''

#define LED groups
line_one = 190
line_two = 161
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(board.D18, line_one, brightness=1, auto_write=False, pixel_order=ORDER)
pixels_bottom = neopixel.NeoPixel(board.D21, line_two, brightness=1, auto_write=False, pixel_order=ORDER)
bottom_box6 = [*range(1117, 1126)]
bottom_box5 = [*range(1108, 1117)]
bottom_box4 = [*range(1099, 1108)]
bottom_box3 = [*range(1090, 1099)]
bottom_box2 = [*range(1081, 1090)]
bottom_box1 = [*range(1072, 1081)]
top_box1 = [*range(1063, 1072)]
top_box2 = [*range(1054, 1063)]
top_box3 = [*range(1045, 1054)]
top_box4 = [*range(1036, 1045)]
top_edge = [*range(1000, 1036)]
left_shelf = [*range(0, 71)]
right_shelf = [*range(71, 142)]
workbench_top = [*range(142, 190)]
workbench_bottom = [*range(1126, 1161)]
section1 = left_shelf + top_box3 + top_box1 + bottom_box2 + bottom_box4 + bottom_box6
section2 = right_shelf + top_box4 + top_box2 + bottom_box1 + bottom_box3 + bottom_box5 + workbench_bottom
section3 = workbench_top + top_edge

#Color Wheel for cycling colors
def wheel(pos):
  if pos < 0 or pos > 255:
    r = g = b = 0
  elif pos < 85:
    r = int(pos * 3)
    g = int(255 - pos * 3)
    b = 0
  elif pos < 170:
    pos -= 85
    r = int(255 - pos * 3)
    g = 0
    b = int(pos * 3)
  else:
    pos -= 170
    r = 0
    g = int(pos *3)
    b = int(255 - pos * 3)
  return(r, g, b)

def rainbow_cycle(wait):
  for j in range(wait):
    for i in range(line_one):
      pixel_index = (i * 256 // line_one) + j
      pixels[i] = wheel(pixel_index & 255)
    for i in range(line_two):
      pixel_index = (i * 256 // line_two) + j
      pixels_bottom[i] = wheel(pixel_index & 255)
    show_all()
    sleep(0.005)

def block_set(p, r, g, b):
  for i in p:
    if i < 1000:
      pixels[i] = (r, g, b)
    else:
      i = i - 1000
      pixels_bottom[i] = (r, g, b)

def wee_woo(l):
  for k in range(l):
    for j in range(20):
      if j < 5:
        block_set(section1, 255, 0, 0)
        block_set(section2, 0, 0, 0)
        block_set(section3, 255, 255, 255)
        show_all()
        sleep(0.04)
        block_set(section3, 0, 0, 0)
        show_all()
        sleep(0.04)
        block_set(section1, 0, 0, 0)
        block_set(section2, 0, 0, 255)
        block_set(section3, 255, 255, 255)
        show_all()
        sleep(0.04)
        block_set(section3, 0, 0, 0)
        show_all()
        sleep(0.04)
      elif 5 < j < 10:
        block_set(section1, 255, 0, 0)
        block_set(section2, 0, 0, 0)
        block_set(section3, 0, 0, 0)
        show_all()
        sleep(0.04)
        block_set(section3, 0, 0, 0)
        show_all()
        sleep(0.04)
        block_set(section1, 0, 0, 0)
        block_set(section2, 0, 0, 255)
        block_set(section3, 0, 0, 0)
        show_all()
        sleep(0.04)
        block_set(section3, 0, 0, 0)
        show_all()
        sleep(0.04)
      elif 10 < j < 15:
        block_set(section1, 0, 0, 255)
        block_set(section2, 0, 0, 0)
        block_set(section3, 255, 255, 255)
        show_all()
        sleep(0.04)
        block_set(section3, 0, 0, 0)
        show_all()
        sleep(0.04)
        block_set(section1, 0, 0, 0)
        block_set(section2, 255, 0, 0)
        block_set(section3, 255, 255, 255)
        show_all()
        sleep(0.04)
        block_set(section3, 0, 0, 0)
        show_all()
        sleep(0.04)
      else:
        block_set(section1, 0, 0, 255)
        block_set(section2, 0, 0, 0)
        block_set(section3, 0, 0, 0)
        show_all()
        sleep(0.04)
        block_set(section3, 0, 0, 0)
        show_all()
        sleep(0.04)
        block_set(section1, 0, 0, 0)
        block_set(section2, 255, 0, 0)
        block_set(section3, 0, 0, 0)
        show_all()
        sleep(0.04)
        block_set(section3, 0, 0, 0)
        show_all()
        sleep(0.04)

def set_all(r, g, b):
  pixels.fill((r, g, b))
  pixels_bottom.fill((r, g, b))

def show_all():
  pixels.show()
  pixels_bottom.show()

def strobe(l):
  set_all(0, 0, 0)
  show_all()
  for i in range(l):
    set_all(255, 255, 255)
    show_all()
    sleep(0.05)
    set_all(0, 0, 0)
    show_all()
    sleep(0.05)

def chillin():
  set_all(40, 30, 200)
  block_set(top_edge, 200, 0, 200)
  block_set(workbench_top, 30, 0, 60)
  block_set(left_shelf, 145, 0, 255)
  block_set(right_shelf, 145, 0, 255)
  show_all()

def multi_color():
  #Red (70, 10, 10)
  #Green (0, 100, 0)
  #Light Green (50, 100, 20)
  #Blue (40, 40, 70)
  #Light Blue (30, 60, 80)
  #Orange (104, 45, 0)
  #Yellow (100, 75, 0)
  #Violet (70, 25, 70)
  #Twitch Purple (145, 70, 255)
  #Under Desk
  block_set(workbench_bottom, 255, 0, 0)
  #Bottom Box 6
  block_set(bottom_box6, 100, 75, 0)
  #Bottom Box 5
  block_set(bottom_box5, 15, 100, 15)
  #Bottom Box 4
  block_set(bottom_box4, 80, 10, 10)
  #Bottom Box 3
  block_set(bottom_box3, 80, 55, 80)
  #Bottom Box 2
  block_set(bottom_box2, 104, 45, 0)
  #Bottom Box 1
  block_set(bottom_box1, 30, 60, 80)
  #Top Box 1 Left Edge
  block_set(workbench_top, 70, 0, 150)
  #Top Box 1
  block_set(top_box1, 70, 10, 10)
  #Top Box 2
  block_set(top_box2, 104, 0, 45)
  #Top Box 3
  block_set(top_box3, 0, 100, 0)
  #Top Box 4
  block_set(top_box4, 0, 25, 100)
  #Top edge
  block_set(top_edge, 0, 100, 35)
  #Left Shelf
  block_set(left_shelf, 255, 20, 147)
  #Right Shelf
  block_set(right_shelf, 25, 147, 255)
  show_all()

def flash_alert(l, r, g, b):
  for i in range(l):
    set_all(r, g, b)
    for j in range(10):
      block_set(top_edge, 255, 255, 255)
      block_set(workbench_top, 255, 255, 255)
      show_all()
      sleep(0.04)
      block_set(top_edge, 0, 0, 0)
      block_set(workbench_top, 0, 0, 0)
      show_all()
      sleep(0.04)
      if j >= 5:
        set_all(0,0,0)
        show_all()
  set_all(r, g, b)
  show_all()

'''
#while listener for
while True:
  msg = lumia_ws.recv()
  print(msg)
'''
chillin()
while True:
  prompt_input = input("1) Wee-Woo\n2) chillin\n3) Multi-Colored\nr) Reboot\nx) Exit\nEnter Selection: ")
  if prompt_input == '1':
    redeem_color('wee-woo (10 seconds)')
  elif prompt_input == '2':
    redeem_color('chillin')
  elif prompt_input == '3':
    redeem_color('Multi-Colored')
  elif prompt_input == 'r':
    pubsub.stop()
    pubsub.start()
    print('pubsub reloaded')
  elif prompt_input == 'x':
    pubsub.stop()
    sys.exit()