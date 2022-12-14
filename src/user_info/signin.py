import hashlib
import pymysql as mysql

import jwt

import os
from dotenv import load_dotenv

load_dotenv()

def SQLConnection(sql_conn, database):
    sql_conn = sql_conn.connect(
            host        = 'localhost',   # 루프백주소, 자기자신주소
            user        = os.environ.get('DB_USER'),        # DB ID      
            password    = os.environ.get('DB_PW'),    # 사용자가 지정한 비밀번호
            database    = database,
            charset     = 'utf8',
            # cursorclass = sql.cursors.DictCursor #딕셔너리로 받기위한 커서
        )
    return sql_conn

def checkDuplicated(column, data):
    sql_conn = mysql
    sql_conn = SQLConnection(sql_conn, os.environ.get('DB_DB'))

    sql = sql_conn.cursor()

    sql_query = f"SELECT COUNT(*) FROM `{os.environ.get('TABLE_USER')}` WHERE `{column}`='{data}'"
    sql.execute(sql_query)
    cnt = sql.fetchone()[0]

    sql_conn.close()

    # 201 : 중복된 데이터 없음
    # 202 : 중복된 데이터 있음
    if cnt == 0:
        return 201
    return 202

def sqlSelect(sql_query):
    sql_conn = mysql
    sql_conn = SQLConnection(sql_conn, os.environ.get('DB_DB'))

    sql = sql_conn.cursor()

    sql.execute(sql_query)
    row = sql.fetchone()

    sql_conn.close()

    return row

def createJWT(id, pw, name, login):
    payload = {
        'id': id,
        'pw': pw,
        'name': name,
        'login': login
    }

    token = jwt.encode(payload, os.environ.get("JWT_SECRET_KEY"), algorithm=os.environ.get('JWT_ALGO'))

    return token

def isValidToken(token):
    try:
        payload = jwt.decode(token, os.environ.get('JWT_SECRET_KEY'), algorithms=[os.environ.get('JWT_ALGO')])
    except:
        return False

    sql_query = f"""SELECT `token` FROM `{os.environ.get('TABLE_USER')}` WHERE id=\'{payload['id']}\'"""
    token_db = sqlSelect(sql_query)

    return token.split(".")[-1] == token_db[0]

def isInDB(token):
    payload = jwt.decode(token, os.environ.get('JWT_SECRET_KEY'), algorithms=[os.environ.get('JWT_ALGO')])

    sql_query = f"SELECT pw FROM `{os.environ.get('TABLE_USER')}` WHERE id=\'{payload['id']}\'"
    row = sqlSelect(sql_query)

    return row is not None and payload['pw'] == row[0]

def signIn(args):
    id = args.get('id')
    pw = args.get('pw')
    token = args.get('token')

    """     if token != "":

        if not isValidToken(token):
            return {'res_code': 502, 'token': ""} # invalid token

        if not isInDB(token):
            return {'res_code': 502, 'token': ""} # invalid token

        return {'res_code': 201, 'token': token} # valid token. login with token """
    
    if checkDuplicated('id', id) == 201:
        return {'res_code': 500, 'token': ""} # not in database

    t = pw
    for _ in range(int(os.environ.get("SHA_REPEAT"))):
        t = hashlib.sha512(t.encode()).hexdigest()

    sql_query = f"SELECT id, pw, name, type FROM `{os.environ.get('TABLE_USER')}` WHERE id='{id}'"
    row = sqlSelect(sql_query)

    if t != row[1]:
        return {'res_code': 501, 'token': ""} # password is not correct

    token = createJWT(row[0], row[1], row[2], row[3])

    return {'res_code': 201, 'token': token} # login with id/pw