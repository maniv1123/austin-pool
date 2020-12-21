import os
import time
import re
from flask import request
from flask import Flask, render_template, jsonify, json
import mysql.connector
from mysql.connector import errorcode


application = Flask(__name__)
app = application

def get_db_creds():
    db = os.environ.get("DB", None) or os.environ.get("database", None)
    username = os.environ.get("USER", None) or os.environ.get("username", None)
    password = os.environ.get("PASSWORD", None) or os.environ.get("password", None)
    hostname = os.environ.get("HOST", None) or os.environ.get("dbhost", None)
    return db, username, password, hostname


def create_table():
    # Check if table exists or not. Create and populate it only if it does not exist.
    db, username, password, hostname = get_db_creds()
    table_ddl = 'CREATE TABLE pool_data(pool_name VARCHAR (100), status TEXT, phone TEXT, pool_type TEXT, PRIMARY KEY (pool_name))'

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname,
                                      database=db)
    except Exception as exp:
        print(exp)
        raise

    cur = cnx.cursor()

    try:
        cur.execute(table_ddl)
        cnx.commit()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)


def populate_data():

    db, username, password, hostname = get_db_creds()

    print("Inside populate_data")
    print("DB: %s" % db)
    print("Username: %s" % username)
    print("Password: %s" % password)
    print("Hostname: %s" % hostname)

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                       host=hostname,
                                       database=db)
    except Exception as exp:
        print(exp)
        raise

    cur = cnx.cursor()
    cur.execute("INSERT INTO pool_data (pool_name) values ('Hello, Pools!')")
    cnx.commit()
    print("Returning from populate_data")


def query_data(pool_name):

    db, username, password, hostname = get_db_creds()

    print("Inside query_data")
    print("DB: %s" % db)
    print("Username: %s" % username)
    print("Password: %s" % password)
    print("Hostname: %s" % hostname)

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname,
                                      database=db)
    except Exception as exp:
        print(exp)
        raise

    cur = cnx.cursor()

    cur.execute("SELECT * FROM pool_data WHERE pool_name = '{}'".format(pool_name))
    # returns a list of tuples, will have 0 or 1 elements
    entries = cur.fetchall()
    return entries

try:
    print("---------" + time.strftime('%a %H:%M:%S'))
    print("Before create_table global")
    create_table()
    print("After create_data global")
except Exception as exp:
    print("Got exception %s" % exp)
    conn = None

@app.route("/")
def pool_info_website():
    return render_template('index.html')

@app.route('/static/add_pool', methods=['POST'])
def add_to_db():
    print("Received request.")
    #msg = request.json
    pool_name1 = request.form['pool_name']
    status1 = request.form['status']
    phone1 = request.form['phone']
    pool_type1 = request.form['pool_type']
    db, username, password, hostname = get_db_creds()

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname,
                                      database=db)
    except Exception as exp:
        print(exp)
        raise

    cur = cnx.cursor()
    cur.execute("INSERT INTO pool_data (pool_name, status, phone, pool_type) VALUES  (%s, %s, %s, %s)",(pool_name1,status1,phone1,pool_type1))
    cnx.commit()

    return render_template('pool_added.html')

@app.route('/pools', methods=['GET'])
def check_database():
    db, username, password, hostname = get_db_creds()

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname,
                                      database=db)
    except Exception as exp:
        print(exp)
        raise

    cur = cnx.cursor()
    all_pools =[]

    cur.execute("SELECT * FROM pool_data")
    result = cur.fetchall()
    for row in result:
        pool = {}
        pool['Name'] = row[0]
        pool['Status'] = row[1]
        pool['Phone'] = row[2]
        pool['Type'] = row[3]
        all_pools.append(pool)

    return json.dumps(all_pools)

@app.route('/pools/<pname>', methods=['PUT'])
def update_database(pname):
    msg = request.json
    pool_name2 = msg['pool_name']
    status2 = msg['status']
    phone2 = msg['phone']
    pool_type2 = msg['pool_type']
    db, username, password, hostname = get_db_creds()

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname,
                                      database=db)
    except Exception as exp:
        print(exp)
        raise

    cur = cnx.cursor()
    cur.execute("SELECT * FROM pool_data WHERE pool_name = %s", (pname,))
    data = cur.fetchall()

    if not (re.match("[0-9]{3}-[0-9]{3}-[0-9]{4}", phone2)):
        return 'Message: phone field not in valid format', 400

    if (status2 != 'Closed' and status2 != 'Open' and status2 !=  'In Renovation'):
        return 'Message: status field has invalid value', 400

    if (pool_type2 != 'Neighborhood' and pool_type2 != 'University' and pool_type2 !=  'Community'):
        return 'Message: pool_type field has invalid value', 400

    if (len(data)==0):
        return 'Message: Pool with name '+ str(pname) + ' does not exist', 404

    if (len(data)!=0):
        if (pool_name2 != pname):
            return 'Message: Update to pool_name field not allowed', 400
        else:
            cur.execute("UPDATE pool_data SET status = %s, phone = %s, pool_type= %s WHERE pool_name = %s;", (status2, phone2, pool_type2,pname,))
            cnx.commit()
            return msg, 200

@app.route('/pools/<pname>', methods=['DELETE'])
def delete_database(pname):
    db, username, password, hostname = get_db_creds()

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname,
                                      database=db)
    except Exception as exp:
        print(exp)
        raise

    cur = cnx.cursor()
    cur.execute("SELECT * FROM pool_data WHERE pool_name = %s", (pname,))
    data = cur.fetchall()

    if (len(data)==0):
        return 'Message: Pool with name '+ str(pname) + ' does not exist', 404
    else:
        cur.execute("DELETE FROM pool_data WHERE pool_name= %s;", (pname,))
        cnx.commit()
        return '', 200

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')