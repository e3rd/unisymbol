#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# development
#
#
#
""" Pomocny podskript pripravi soubor unicode.
# Zpracovava soubor se znaky unicodu, stazeny z ftp://ftp.unicode.org/Public/UNIDATA/NamesList.txt a dela z toho vstup pro muj skript unisymbol.
# Vstup:
#000E	<control>
#	= SHIFT OUT
#	* known as LOCKING-SHIFT ONE in 8-bit environments
#
# Vystup: <control> = SHIFT OUT [tab] 000E
#

result = []
new = []
i = 0
with open('/home/edvard/Downloads/NamesList.txt', 'r') as f:
    for line in f.read().splitlines():#.readlines():
        #i+=1
        #if i > 10:
        #    break
        line = line.strip().replace("\t"," ")
        first = line[0]
        if first == "=": # inteligentne pripoji dalsi informace k lince - ignoruje vsechna slova, ktera se uz na ni uz vyskytuji
            words = new[-1].lower().split(" ")
            for word in line.lower().split(" "):
                if word not in words:
                    new[-1] += " " + word
        elif first in ("*", "~","x","@", "#", ":"):
            continue
        else:
            new.append(line)
# transormace radku -> dat unicode kod na konec
for l in new:
    s = l.split(" ",1)
    t = s[1] + "\t" + s[0]
    result.append(t)
with open("new.txt",'w') as f:
    f.write("\n".join(result))
"""
UNICODE_FILE = '/home/edvard/unicode.txt'

#importy
import configparser
import re
import select
import subprocess
import sys
import termios
import time
import tty

#subprocess.Popen('xdotool key alt+Tab', shell=True)
#subprocess.Popen('xdotool key U2132 &', shell=True)

launchInternal = False
try:
    print(termios.tcgetattr(sys.stdin))
    launchInternal = True
    #subprocess.Popen(["grep", line, UNICODE_FILE], stdout=subprocess.PIPE)

except:
    #print(e)
    #print("nelze")
    # mohlo by to spoustet samo sebe, ale spatne to funguje
    #subprocess.Popen('eval $(xdotool getmouselocation --shell)',shell=True)
    #time.sleep(0.5)

    process = subprocess.Popen('gnome-terminal --title=unisymbol -e unisymbol.py --hide-menubar --geometry=100x43+$X+$Y', shell=True,stdout=subprocess.PIPE)
    #s = subprocess.check_call('gnome-terminal --title=unisymbol --hide-menubar --geometry=80x23+$X+$Y -x bash -c unisymbol.py', shell=True)
    #process.communicate()
    #process.wait()
    #s = str(process.communicate()[0], "utf-8")#.split("\n")[:-1]
    #time.sleep(0.5)
    #subprocess.Popen('notify-send ab ' +str(s),shell=True)
    #subprocess.Popen('notify-send '+str(s),shell=True)
    #time.sleep(0.5)
    #subprocess.Popen('xdotool key U2132 &', shell=True) # && ', shell=True)
    exit(0)


if launchInternal:
        sys.stdout.write("\033c") #clear screen, je kdoviproc necim zaneradena

        #funkce na read stdin
        def getkey():
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
            select.select([sys.stdin], [], [], 0)
            answer = sys.stdin.read(1)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            return answer



        #init
        query = "" #prikaz uzivatele
        caret = {'pos':0, 'altPos':0, 'text':""}  #pozice kurzoru
        matches = [] # XX lze sem dat recentne pouzite

        #engine
        while 1:
            #init
            print("\x1B[3m" + (query if query else " ** character description **") + "\x1B[23m")# italikem vypsat prikaz
            menu = [] #mozne prikazy uzivatele
            caret['altPos'] = 0 #mozne umisteni karetu - na zacatek

            if query: #grepujeme case insensitive a za kazde slovo dame wildcard
                subquery = ""
                subquery = "[^\s]* ".join(query.split(" "))
                #for word in query.split(" "):
                #    subquery += word + "[^\s]* "
                process = subprocess.Popen("grep -i '" + "[^\s]* ".join(query.split(" ")) + "' " +  UNICODE_FILE + " | head -n 40", stdout=subprocess.PIPE, shell=True)
                matches = str(process.communicate()[0], "utf-8").split("\n")[:-1]
    
                used = set()
                #i = 0
                for option in matches:                    
                    try:
                        if option[:len("<control>")] == "<control>":
                            ch = "N/A"
                        else:
                            ch = chr(int(option.split("\t")[-1], 16))
                    except ValueError: #je mozne, nektere znaky unikodu proste nevytiskneme
                        print("-- znak nelze tisknout -- ")
                        continue
                        #ch = #"x"+option.split("\t")[-1]
                    #print(ch)
                    if ch not in used: # muze se stat, ze je v listu nejaky unicode znak dvakrat
                        used.add(ch)
                        option += " " + ch
                        menu.append(option) #zaradit mezi moznosti
                        if option == caret['text']: #karet byl na tehle pozici, pokud se zuzil vyber, budeme vedet, kam karet opravne umistit
                            caret['altPos'] = len(menu)-1
                    #i += 1
                    #if i > 40:
                    #    break
                    #uprint(matches)
                        #if len(used) == 1:
                        # print("VYBRANO: " + used.pop())

            #osetrit vychyleni karetu
            if caret['pos'] < 0 or caret['pos'] > len(menu)-1: #umistit karet na zacatek ci konec seznamu
                caret['pos'] = caret['altPos']

            #vypsat menu
            #print("caret:" + str(caret['pos']))
            for i in range(0, len(menu)):
                if i == caret['pos']: #karet je na pozici
                    caret['text'] = menu[i]
                    print('\033[1m' + menu[i] + '\033[0m')#vypsat moznost tucne
                else:
                    try:
                        print(menu[i])
                    except:
                        print("CHYBA")
                        print(menu[i][0:-1])
            #print("query" + query)
            #print("list:"+ list(config['MENU'])[caret])
            stop = False
            #vyhodnotit moznost
            if len(menu) != 1: #stale mame vic moznosti
                key = getkey()

                if ord(key) == 27: #escape sequence
                    print("Hit escape for exit...") #pokud jsem predtim napsal sipku, dalsi 2 znaky automaticky cekaji
                    key = getkey()
                    if ord(key) == 27: #dvojity escape - ukonceni
                        exit()
                    elif ord(key) == 91: #sipka
                        key = getkey()
                        if ord(key) == 65: #sipka nahoru
                            caret['pos'] -= 1
                        if ord(key) == 66: #sipka dolu
                            caret['pos'] += 1
                    elif ord(key) == 79: #home/end
                        key = getkey()
                        if ord(key) == 72: #home
                            caret['pos'] = 0
                        if ord(key) == 70: #end
                            caret['pos'] = len(menu) -1
                    else:
                        print("NIC!")
                elif(key == '\x08' or key == '\x7f'):#backspace
                    caret['pos'] = -1
                    query = query[:-1]
                elif(ord(key) == 13): #enter
                    menu = [menu[caret['pos']]] #launch command at caret
                elif(key == '\x03' or key == '\x04'):#interrupt  (zel nefunguje)
                    exit()
                elif(49 <= ord(key) <= 57):#cisla spousti prikaz na danem radku
                    menu = [menu[ord(key)-49]]
                    #query = menu[ord(key)-49] #launch command at number
                else:
                    print("ZDE")
                    caret['pos'] = -1
                    query += key

            if stop:
                print("l", len(menu))
                exit(0)


            if len(menu) == 1: #vybrana 1 moznost ke spusteni
                sys.stdout.write("\033c");#clear terminal
                #c = menu[0]
                sys.stdout.write("\x1b]0;" + menu[0] + "\x07") #gnome-terminal title
                result = menu[0].split(" ")[-1] # + result
                print(result)
                print(hex(ord(result)).split('x')[1])                
                subprocess.Popen('xdotool key alt+Tab && xdotool key U' + hex(ord(result)).split('x')[1] + ' &', shell=True) #spusti podproces, odpoji ho od terminalu. Ten balast na konci je pro silent start nohupu.

                #ihned skoncit, at muzu dal psat time.sleep(0.5)
                time.sleep(0.5) # xdotool musi mit cas se napsat -> kdyz skoncim moc brzo, xdotool se nepovede. Zatim je to tahle klicka.
                #getkey()
                exit(0)
                #sys._exit(0)
            sys.stdout.write("\033c") #clear screen

    