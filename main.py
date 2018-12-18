import os, os.path
import random
import sqlite3
import string
import time
import cherrypy
import Adafruit_BBIO.GPIO as GPIO
from setuptools.command.saveopts import saveopts

diodePin = ["P8_7", "P8_8", "P8_9", "P8_10"]
buttonPin = ["P8_15", "P8_16", "P8_17", "P8_18"]
GPIO.setup("P8_7", GPIO.OUT)
GPIO.setup("P8_8", GPIO.OUT)
GPIO.setup("P8_9", GPIO.OUT)
GPIO.setup("P8_10", GPIO.OUT)
GPIO.setup("P8_15", GPIO.IN)
GPIO.setup("P8_16", GPIO.IN)
GPIO.setup("P8_17", GPIO.IN)
GPIO.setup("P8_18", GPIO.IN)

DB_STRING = "my.db"
global tabela
generator = 0


def generate(count):
    generated = []
    for i in range(count):
        number = random.randint(0, 3)
        diode = diodePin[number]
        generated.append(number)
        GPIO.output(diode, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(diode, GPIO.LOW)
        time.sleep(0.2)
    return generated


def wrong():
    for i in diodePin:
        GPIO.output(i, GPIO.HIGH)
    time.sleep(0.5)
    for i in diodePin:
        GPIO.output(i, GPIO.LOW)


def correct():
    for i in diodePin:
        GPIO.output(i, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(i, GPIO.LOW)


def check(sequence, count):
    number = 5
    for i in range(count):
        while True:
            if GPIO.input("P8_15") == 1:
                print('0')
                GPIO.output("P8_7", GPIO.HIGH)
                time.sleep(0.3)
                GPIO.output("P8_7", GPIO.LOW)
                number = 0
                break
            elif GPIO.input("P8_16") == 1:
                print('1')
                GPIO.output("P8_8", GPIO.HIGH)
                time.sleep(0.3)
                GPIO.output("P8_8", GPIO.LOW)
                number = 1
                break
            elif GPIO.input("P8_17") == 1:
                print('2')
                GPIO.output("P8_9", GPIO.HIGH)
                time.sleep(0.3)
                GPIO.output("P8_9", GPIO.LOW)
                number = 2
                break
            elif GPIO.input("P8_18") == 1:
                print('3')
                GPIO.output("P8_10", GPIO.HIGH)
                time.sleep(0.3)
                GPIO.output("P8_10", GPIO.LOW)
                number = 3
                break

        if sequence[i] == number:
            continue

        else:
            wrong()
            return False
    correct()
    return True


@cherrypy.expose
class serviceDB(object):

    @cherrypy.tools.accept(media='text/plain')
    def create(self):
        with sqlite3.connect(DB_STRING) as c:
            r = c.execute("CREATE TABLE IF NOT EXISTS ranking (nazwa varchar(40), level integer, data varchar(40))")

    def GET(self):
        with sqlite3.connect(DB_STRING) as c:
            # cherrypy.session['ts'] = time.time()
            r = c.execute("SELECT nazwa, level, data FROM ranking ORDER BY level desc")
            return r.fetchall()

    def POST(self, nazwa, level, data):
        with sqlite3.connect(DB_STRING) as c:
            c.execute("INSERT INTO ranking VALUES (?, ?, ?)", [nazwa, level, data])
            c.commit()

    def PUT(self, another_string):
        with sqlite3.connect(DB_STRING) as c:
            cherrypy.session['ts'] = time.time()
            c.execute("UPDATE user_string SET value=? WHERE session_id=?",
                      [another_string, cherrypy.session.id])

    def DELETE(self):
        cherrypy.session.pop('ts', None)
        with sqlite3.connect(DB_STRING) as c:
            c.execute("DELETE FROM user_string WHERE session_id=?",
                      [cherrypy.session.id])


class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        return """<html>
         <head></head>
         <body>
           <form method="get" action="play">
             <input type="text" value="Login" name="user" />
             <button type="submit">Graj!</button>
           </form>
         </body>
       </html>"""

    @cherrypy.expose
    def play(self, user="NEW"):
        while GPIO.input("P8_15") == 0:
            for i in diodePin:
                GPIO.output(i, GPIO.HIGH)
                time.sleep(0.5)
            for i in diodePin:
                GPIO.output(i, GPIO.LOW)
        time.sleep(1)
        lvl = 1
        count = 4
        while True:
            sequence = generate(count)
            print(sequence)
            if check(sequence, count) == True:
                lvl += 1
                count += 1
                print('Congratulations. You completed level ' + str(lvl) + '!!! Its time for next level in 0.5 seconds')
                time.sleep(1)
                continue
            else:
                print("You lost!!! You reached level " + str(lvl) + ".")
                time.sleep(0.5)
                break

        data = time.asctime(time.localtime(time.time()))
        generator.POST(user, lvl, data)
        global tabela
        tabela = generator.GET()
        print("play")
        return self.rank()

    @cherrypy.expose
    def rank(self, user="NEW"):
        print("rank")
        rekord = ""
        i = 0
        for t in tabela:
            i += 1
            rekord += """
           <tr>
               <td class="tg-0lax">""" + str(i) + """</td>
               <td class="tg-0lax">""" + t[0] + """</td>
               <td class="tg-0lax">""" + str(t[1]) + """</td>
               <td class="tg-0lax">""" + t[2] + """</td>
             </tr>"""

        some_string = """<html>
         <head></head>
         <body>
           <style type="text/css">
           .tg  {text-align:center; margin-top:100px; margin-left:auto; margin-right:auto; width:400px;border-collapse:collapse;border-spacing:0;}
           .tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
           .tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
           .tg .tg-ark5{font-weight:bold;background-color:#003532;color:#efefef;text-align:left;vertical-align:top}
           .tg .tg-0lax{text-align:left;vertical-align:top}
           </style>
           <form method="get" action="index">
             <button type="submit">Powrót</button>
           </form>
           <table class="tg" align="center">
             <tr>
               <th class="tg-ark5">LP</th>
               <th class="tg-ark5">Nazwa</th>
               <th class="tg-ark5">Level</th>
               <th class="tg-ark5">Data</th>
             </tr>""" + rekord + """</table>

         </body>
       </html>"""
        cherrypy.session['mystring'] = some_string
        return some_string

    @cherrypy.expose
    def display(self):
        return cherrypy.session['mystring']


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True
        }
    }
    generator = serviceDB()
    generator.create()
    tabela = generator.GET()

    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.quickstart(StringGenerator(), '/', conf)