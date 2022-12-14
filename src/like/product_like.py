import pymysql as mysql

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

def modifyProductLike(sql_conn, args):
    vender = args.get('vender')
    pName = args.get('pName').strip()
    flag = args.get('flag') # like or unlike
    table = os.environ.get("TABLE_LIKE")

    sql_query = f"""
UPDATE {table}
SET `like`=`like`+({1 if flag == "like" else -1})
WHERE
	vender="{vender}" AND
	pName= (SELECT R.pName
				FROM (
						SELECT pName
						FROM {table}
						WHERE
							INSTR(pName, "{pName}")>0 AND INSTR(vender, "{vender}")>0
					) R
				)
    """ + ";"

    sql_conn = SQLConnection(sql_conn, os.environ.get("DB_DB"))
    sql = sql_conn.cursor()

    sql.execute(sql_query)
    sql_conn.commit()

    sql_conn.close()

    res_code = 201

    return {'res_code': res_code}

def getProductLikeList(sql_conn):
    MAX_CNT = 10
    table = os.environ.get("TABLE_LIKE")

    # vender, pName, like
    # sql_query = f"""Select *
    # From {table}
    # WHERE `like`>0
    # Order BY `like` desc
    # Limit {MAX_CNT}""" + ";"

    # ranking = {}
    # for row in rows:
    #     name = f"{row[0]}&{row[1]}"
    #     ranking[name] = row[2]

    sql_query = f"""
    SELECT vender, pType, pName, pPrice, pImg, `like` 
    FROM 
        (SELECT *
            FROM {os.environ.get("TABLE_LIKE")}
            WHERE `like`>0
            LIMIT {MAX_CNT}
        ) PL
        NATURAL JOIN
        {os.environ.get("TABLE_CRAWLING")}
    """ + ";"


    sql_conn = SQLConnection(sql_conn, os.environ.get("DB_DB"))
    sql = sql_conn.cursor()

    sql.execute(sql_query)
    rows = sql.fetchall()

    sql_conn.close()

    ranking = {}
    for row in rows:
        name = f"{row[0]}&{row[2]}"
        ranking[name] = {'pType': row[1], 'pPrice': row[3], 'pImg': row[4], 'like': row[5]}

    return ranking

