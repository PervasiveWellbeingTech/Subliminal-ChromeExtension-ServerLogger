#!/usr/bin/env python
# Reflects the requests from HTTP methods GET, POST, PUT, and DELETE
# Written by Nathan Hamiel (2010)
# Modified by Marco Mora-Mendoza

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from optparse import OptionParser
import sqlite3
from sqlite3 import Error
import json
import datetime

database = r"C:\sqlite\db\BreathingEdgesLog.db"

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        request_path = self.path
        print("\n----- Request Start ----->\n")
        print(request_path)
        print(self.headers)
        print("<----- Request End -----\n")

        # Respond to id request
        if request_path == '/getID':
            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()
            self.wfile.write(get_new_user_id())
        else:
            self.send_response(200)


    def do_POST(self):

        request_path = self.path

        print("\n----- Request Start ----->\n")
        #print(request_path)
        request_headers = self.headers
        content_length = request_headers.getheaders('content-length')
        length = int(content_length[0]) if content_length else 0
        #print(request_headers)
        print("-------------BODY START----------------")
        body = self.rfile.read(length)
        dict = json.loads(body)
        # Add activity to table
        act = (dict["user_id"], dict['Action'], dict['New value'], dict['url'], dict['time'])
        print(act)
        activity_id = create_activity(act)
        print("<----- Request End -----\n")

        self.send_response(200)

    do_PUT = do_POST
    do_DELETE = do_GET

# Searches user_ids table for largest value
# Adds this value + 1 to user_ids table and returns the incremented value
# Returns 1 if no ids in table
def get_new_user_id():
    try:
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute(''' SELECT MAX(id) FROM user_ids''')
        last_user_id = cur.fetchone()
        id = last_user_id[0]
        if(id == None):
            id = 1
        else:
            id += 1
        set_user_id(id)
        cur.close()
        return id
    except Error as e:
        print(e)

# Adds id_num and current time to user_ids table
def set_user_id(id_num):
    try:
        date = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        input_info = (id_num, date)
        sql = ''' INSERT INTO user_ids(id, date_created)
                  VALUES(?,?) '''
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute(sql, input_info)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(e)

# Adds act into activity table
# act is a tuple of (user_id, action, value, url, time)
def create_activity(act):
    try:
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        sql = ''' INSERT INTO activity(user_id, action, value, url, time)
                  VALUES(?,?,?,?,?) '''
        cur.execute(sql, act)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(e)

# Adds table to database from create_table_sql CREATE TABLE statement
def create_table(create_table_sql):
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def main():
    try:
        conn = sqlite3.connect(database)
    except Error as e:
        print(e)
    if conn is not None:
        print("Successful connection to database.")
        # Create activity and id tables in database
        sql_activity_table = """ CREATE TABLE IF NOT EXISTS activity (
                                        user_id integer,
                                        action text,
                                        value text,
                                        url text,
                                        time text
                                    ); """

        sql_id_table = """ CREATE TABLE IF NOT EXISTS user_ids (
                                        id integer PRIMARY KEY,
                                        date_created text
                                    ); """
        create_table(sql_activity_table)
        create_table(sql_id_table)
    else:
        print("Error! cannot create the database connection.")

    port = 8080
    print('Listening on localhost:%s' % port)
    server = HTTPServer(('', port), RequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    parser = OptionParser()
    parser.usage = ("Creates an http-server that will echo out any GET or POST parameters\n"
                    "Run:\n\n"
                    "   reflect")
    (options, args) = parser.parse_args()

    main()
