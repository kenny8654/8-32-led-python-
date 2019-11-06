#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time
import traceback
from rpi_ws281x import *
import argparse
import parse_string as ps
import thread
from beacontools import BeaconScanner, IBeaconFilter
import requests

# LED strip configuration:
LED_COUNT      = 256      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 10     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
user_list = []
count = 0
chat_list = []
chat_count = 0
    
def callback(bt_addr, rssi, packet, additional_info):
    #print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))
    if additional_info and 'uuid' in additional_info: 
        #print(type(int(additional_info['uuid'][-2:])))
        if str(additional_info['uuid'][-3:]) not in user_list:
            user_list.append(str(additional_info['uuid'][-3:]))
            print(user_list)

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def word(w,strip):
    a = ps.slide(w)
    #print(a)
    for leds in a:
        print(leds)
        for i in leds:
            if i >= 0 and i <= 256:
                strip.setPixelColor(i-1,Color(153,102,255))
        print("before show")
        strip.show()
        print("after show")
        time.sleep(0.1)
        for i in  leds:
            if i >= 0 and i <= 256:
                strip.setPixelColor(i-1, Color(0,0,0))
        del leds
    del a
def clock(strip):
    global count,user_list,chat_list,chat_count
    while True:
        print("user",count,len(user_list),"chat",chat_count,len(chat_list))
        if count == len(user_list) and chat_count == len(chat_list):
            print("if")
            t = ps.shift( ps.parse( time.strftime("%H:%M:%S" , time.localtime()),0 ),2)
            print(t)
            for i in t:
                if i >= 0 and i <= 256:
                    strip.setPixelColor(i-1 , Color(128,255,191))
            strip.show() 
            time.sleep(0.5)
            for i in range(256):
                strip.setPixelColor(i,Color(0,0,0))
            del t
            
            r = requests.get('http://140.116.72.90:3000/getList')
            print(r.text,chat_count)
            tmp = r.text.strip('[]').replace('"',"").split(',')
            del chat_list[:]
            for chat in tmp:
                print(str(chat))
                chat_list.append(str(chat))
            #chat_list = r.text.strip('[]').replace('"',"").split(',')
            del r
        else:
            if count != len(user_list):
                print("else")
                for i in range(256):
                    strip.setPixelColor(i,Color(0,0,0))
                print("befor word")    
                word(str(user_list[count]),strip)
                print("after word")
                count = count + 1
                print("after count")
            elif chat_count != len(chat_list):
                print("else")
                for i in range(256):
                    strip.setPixelColor(i,Color(0,0,0))
                print("before word")
                word(str(chat_list[chat_count]),strip)
                print("after word")
                chat_count +=1
                print("after count")
# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    scanner = BeaconScanner(callback,)
    scanner.start()
    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        while True:
            #word("ok",strip)
            #print("into w2")
            #word("hi2",strip)
            clock(strip)
            #word(strip)
            #clock(strip)
            print ('Color wipe animations.')
            colorWipe(strip, Color(255, 0, 0))  # Red wipe
            colorWipe(strip, Color(0, 255, 0))  # Blue wipe
            colorWipe(strip, Color(0, 0, 255))  # Green wipe
            print ('Theater chase animations.')
            theaterChase(strip, Color(127, 127, 127))  # White theater chase
            theaterChase(strip, Color(127,   0,   0))  # Red theater chase
            theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
            print ('Rainbow animations.')
            rainbow(strip)
            rainbowCycle(strip)
            theaterChaseRainbow(strip)

    except KeyboardInterrupt:
        scanner.stop()
        if args.clear:
            colorWipe(strip, Color(0,0,0), 1)
            scanner.stop()
    except:
        print("except")
        traceback.print_exc()
        scanner.stop()
