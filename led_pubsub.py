import board
import neopixel
import requests
import re
import asyncio
import local_auth
from time import sleep
from twitchAPI.twitch import Twitch
from twitchAPI.pubsub import PubSub
from twitchAPI.types import AuthScope
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
    if 'user_input' in data['data']['redemption']:
      user_input = data['data']['redemption']['user_input']
    else:
      user_input = False
    print(user + ' redeemed ' + redeem)
    redeem_color(redeem, user_input)

#Subs via Twitch API
def callback_subs(uuid: UUID, data: dict) -> None:
    global default_redeem
    flash_alert(10, 255, 0, 0)
    redeem_color(default_redeem)

#Bits via Twitch API
def callback_bits(uuid: UUID, data: dict) -> None:
    global default_redeem
    flash_alert(10, 255, 125, 0)
    redeem_color(default_redeem)
    pprint(data)

#Channel Points Redemption Switch
def redeem_color(redeem, u = False):
    global default_redeem
    if redeem == 'wee-woo (10 seconds)':
      wee_woo(3)
      redeem_color(default_redeem)
    elif redeem == 'red':
      pixels.fill((70, 0, 0))
      block_set(left_shelf, 255, 0, 0)
      block_set(right_shelf, 255, 0, 0)
      pixels.show()
      sleep(1)      
      default_redeem = 'red'
    elif redeem == 'green':
      pixels.fill((0, 0, 100))
      block_set(left_shelf, 0, 255, 0)
      block_set(right_shelf, 0, 255, 0)
      pixels.show()
      sleep(1)
      default_redeem = 'green'
    elif redeem == 'blue':
      pixels.fill((40, 70, 40))
      block_set(left_shelf, 0, 0, 255)
      block_set(right_shelf, 0, 0, 255)
      pixels.show()
      sleep(1)
      default_redeem = 'green'
    elif redeem == 'purple':
      pixels.fill((70, 55, 25))
      block_set(left_shelf, 145, 70, 255)
      block_set(right_shelf, 145, 70, 255)
      pixels.show()
      sleep(1)
      default_redeem = 'purple'
    elif redeem == 'aqua':
      pixels.fill((40, 70, 50))
      block_set(left_shelf, 175, 175, 255)
      block_set(right_shelf, 175, 175, 255)
      pixels.show()
      sleep(1)
      default_redeem = 'aqua'
    elif redeem == 'orange':
      pixels.fill((104, 0, 45))
      block_set(left_shelf, 255, 100, 0)
      block_set(right_shelf, 255, 100, 0)
      pixels.show()
      sleep(1)
      default_redeem = 'orange'
    elif redeem == 'Sienna':
      pixels.fill((128, 0, 40))
      pixels.show()
      sleep(1)
      default_redeem = 'Sienna'
    elif redeem == 'Hot Pink':
      pixels.fill((111, 31, 0))
      pixels.show()
      sleep(1)
      default_redeem = 'Sienna'
    elif redeem == 'Multi-Colored':
      multi_color()
      sleep(1)
      default_redeem = 'Multi-Colored'
    elif redeem == 'Strobe (5 seconds)':
      strobe(50)
      redeem_color(default_redeem)
    elif redeem == 'Custom Color':
      rgb_val = hex_to_rgb(u)
      pixels.fill(rgb_val)
      print(rgb_val)
      pixels.show()
      default_redeem = 'Multi-Colored'
    elif redeem == 'Rainbow Puke (10 seconds)':
      rainbow_cycle(800)
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
target_scope = [AuthScope.BITS_READ, AuthScope.CHANNEL_READ_REDEMPTIONS, AuthScope.CHANNEL_READ_SUBSCRIPTIONS]
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
num_pixels = 164
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(board.D18, num_pixels, brightness =1, auto_write=False, pixel_order=ORDER)
table = [*range(0, 27)]
bottom_box6 = [*range(27, 33)]
bottom_box5 = [*range(33, 39)]
bottom_box4 = [*range(39, 45)]
bottom_box3 = [*range(45, 51)]
bottom_box2 = [*range(51, 57)]
bottom_box1 = [*range(57, 63)]
left_edge = [*range(63, 69)]
top_box1 = [*range(69, 75)]
top_box2 = [*range(75, 81)]
top_box3 = [*range(81, 87)]
top_box4 = [*range(87, 93)]
top_edge = [*range(93, 117)]
left_shelf = [*range(117, 140)]
right_shelf = [*range(140, 165)]
zone_array = [table, bottom_box6, bottom_box5, bottom_box4, bottom_box3, bottom_box2, bottom_box1, left_edge, top_box1, top_box2, top_box3, top_box4, top_edge]
section1 = table + bottom_box4 + bottom_box2 + top_box2 + top_box4 + left_shelf
section2 = bottom_box6 + bottom_box5 + bottom_box3 + bottom_box1 + top_box1 + top_box3 + right_shelf
edges = left_edge +  top_edge
nonedges = section1 + section2

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
    for i in range(num_pixels):
      pixel_index = (i * 256 // num_pixels) + j
      pixels[i] = wheel(pixel_index & 255)
    pixels.show()
    sleep(0.005)

def block_set(p, r, g, b):
  for i in range(num_pixels):
    if i in p:
      pixels[i] = (r, b, g)
'''
testing code
def wee_woo_swap(swap_other = False):  
  for i in range(num_pixels):
    if i in section1:
      pixels[i] = (255, 0, 0) if pixels[i] == (0, 0, 0) else (255, 125, 0)
    if i in section2:
      pixels[i] = (0, 255, 0) if pixels[i] == (0, 0, 0) else (0, 125, 255)
    if swap_other and i not in nonedges:
      pixels[i] = (255, 255, 255) if pixels[i] == (255, 255, 255) else (255, 255, 255)

def wee_woo_test(l):
  for i in range(num_pixels):
    if i in section1:
      pixels[i] = (0, 255, 0)
    elif i in section2:
      pixels[i] = (0, 0, 0)
    elif i in edges:
      pixels[i] = (0, 0, 0)
    else:
      pixels[i] = (255, 255, 255)
  for k in range(l):
    for j in range(20):
      if j in [10, 15]:
        wee_woo_swap(True)
      else:
        wee_woo_swap()
      pixels.show()
      sleep(0.08)
      wee_woo_swap()
      pixels.show()
      sleep(0.08)
'''
def wee_woo(l):
  for k in range(l):
    for j in range(20):
      if j < 5:
        for i in range(num_pixels):
          if i in section1:
            pixels[i] = (255, 0, 0)
          elif i in section2:
            pixels[i] = (0, 0, 0)
          else:
            pixels[i] = (255, 255, 255)
        pixels.show()
        sleep(0.04)
        for i in edges:
          pixels[i] = (0, 0, 0)
        pixels.show()
        sleep(0.04)
        for i in range(num_pixels):
          if i in section1:
            pixels[i] = (0, 0, 0)
          elif i in section2:
            pixels[i] = (0, 255, 0)
          else:
            pixels[i] = (255, 255, 255)
        pixels.show()
        sleep(0.04)
        for i in edges:
          pixels[i] = (0, 0, 0)
        pixels.show()
        sleep(0.04)
      elif 5 < j < 10:
        for i in range(num_pixels):
          if i in section1:
            pixels[i] = (255, 0, 0)
          elif i in section2:
            pixels[i] = (0, 0, 0)
          else:
            pixels[i] = (0, 0, 0)
        pixels.show()
        sleep(0.04)
        for i in edges:
          pixels[i] = (0, 0, 0)
        pixels.show()
        sleep(0.04)
        for i in range(num_pixels):
          if i in section1:
            pixels[i] = (0, 0, 0)
          elif i in section2:
            pixels[i] = (0, 255, 0)
          else:
            pixels[i] = (0, 0, 0)
        pixels.show()
        sleep(0.04)
        for i in edges:
          pixels[i] = (0, 0, 0)
        pixels.show()
        sleep(0.04)
      elif 10 < j < 15:
        for i in range(num_pixels):
          if i in section1:
            pixels[i] = (0, 255, 0)
          elif i in section2:
            pixels[i] = (0, 0, 0)
          else:
            pixels[i] = (255, 255, 255)
        pixels.show()
        sleep(0.04)
        for i in edges:
          pixels[i] = (0, 0, 0)
        pixels.show()
        sleep(0.04)
        for i in range(num_pixels):
          if i in section1:
            pixels[i] = (0, 0, 0)
          elif i in section2:
            pixels[i] = (255, 0, 0)
          else:
            pixels[i] = (255, 255, 255)
        pixels.show()
        sleep(0.04)
        for i in edges:
          pixels[i] = (0, 0, 0)
        pixels.show()
        sleep(0.04)
      else:
        for i in range(num_pixels):
          if i in section1:
            pixels[i] = (0, 255, 0)
          elif i in section2:
            pixels[i] = (0, 0, 0)
          else:
            pixels[i] = (0, 0, 0)
        pixels.show()
        sleep(0.04)
        for i in edges:
          pixels[i] = (0, 0, 0)
        pixels.show()
        sleep(0.04)
        for i in range(num_pixels):
          if i in section1:
            pixels[i] = (0, 0, 0)
          elif i in section2:
            pixels[i] = (255, 0, 0)
          else:
            pixels[i] = (0, 0, 0)
        pixels.show()
        sleep(0.04)
        for i in edges:
          pixels[i] = (0, 0, 0)
        pixels.show()
        sleep(0.04)

def strobe(l):
  pixels.fill((0, 0, 0))
  pixels.show()
  for i in range(l):
    pixels.fill((255, 255, 255))
    pixels.show()
    sleep(0.05)
    pixels.fill((0, 0, 0))
    pixels.show()
    sleep(0.05)

def chillin():
  pixels.fill((35, 35, 50))
  block_set(top_edge, 60, 20, 60)
  block_set(left_edge, 60, 20, 60)
  block_set(left_shelf, 145, 60, 255)
  block_set(right_shelf, 145, 60, 255)
  pixels.show()

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
  block_set(table, 70, 10, 10)
  #Bottom Box 6
  block_set(bottom_box6, 100, 75, 0)
  #Bottom Box 5
  block_set(bottom_box5, 15, 100, 15)
  #Bottom Box 4
  block_set(bottom_box4, 70, 10, 10)
  #Bottom Box 3
  block_set(bottom_box3, 70, 55, 70)
  #Bottom Box 2
  block_set(bottom_box2, 104, 45, 0)
  #Bottom Box 1
  block_set(bottom_box1, 30, 60, 80)
  #Top Box 1 Left Edge
  block_set(left_edge, 0, 0, 0)
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
  pixels.show()

def flash_alert(l, r, g, b):
  for i in range(l):
    pixels.fill((r, b, g))
    for j in range(10):
      block_set(top_edge, 255, 255, 255)
      block_set(left_edge, 255, 255, 255)
      pixels.show()
      sleep(0.04)
      block_set(top_edge, 0, 0, 0)
      block_set(left_edge, 0, 0, 0)
      pixels.show()
      sleep(0.04)
      if j >= 5:
        pixels.fill((0,0,0))
        pixels.show()
  pixels.fill((r, b, g))
  pixels.show()

'''
#while listener for
while True:
  msg = lumia_ws.recv()
  print(msg)
'''