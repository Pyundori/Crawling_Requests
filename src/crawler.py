import os
from datetime import datetime
import pymysql as mysql
from crawling import *
from dotenv import load_dotenv

load_dotenv()

def run():
    sql_conn = mysql
    toDatabase(sql_conn)

def makeSQLDatas(vender, vender_name):
    datas = []

    for legend, legend_datas in vender.items():
        for product_name, product_data in legend_datas.items():
            data = []
            data.append(vender_name)

            data.append(legend)
            data.append(product_name)

            data.append(product_data['price'])
            data.append(product_data['img'])

            if product_data['gift'] != None:
                for gift_name, gift_data in product_data['gift'].items():
                    data.append(gift_name)
                    data.append(gift_data['price'])
                    data.append(gift_data['img'])
            else:
                data.append('null')
                data.append(0)
                data.append('null')

            datas.append(data)
    
    return datas

api_func = {
    "gs25": gs25_api,
    "seven_eleven": se_api,
    "cu": cu_api,
    "emart24": emart24_api,
    "ministop": ministop_api, 
}

api_path = {
    "gs25": 'URL_GS25',
    "seven_eleven": 'URL_SE',
    "cu": 'URL_CU',
    "emart24": 'URL_EMART24',
    "ministop": 'URL_MINISTOP', 
}

def toDatabase(sql_conn):
    datas = []

    for key, func in api_func.items():
        data = func(os.environ.get(api_path[key]))
        datas += makeSQLDatas(data, key)

    pushDataToDB(sql_conn, datas)


def SQLConnection(sql_conn):
    sql_conn = sql_conn.connect(
            host        = 'localhost',   # 루프백주소, 자기자신주소
            user        = os.environ.get('DB_USER'),        # DB ID      
            password    = os.environ.get('DB_PW'),    # 사용자가 지정한 비밀번호
            database    = 'crawling',
            charset     = 'utf8',
            # cursorclass = sql.cursors.DictCursor #딕셔너리로 받기위한 커서
        )
    return sql_conn

def pushDataToDB(sql_conn, datas):
    sql_conn = SQLConnection(sql_conn)
    sql = sql_conn.cursor()

    sql_query = "TRUNCATE TABLE crawledData"
    sql.execute(sql_query)
    sql_conn.commit()

    sql_query = "INSERT INTO crawledData (vender, pType, pName, pPrice, pImg, gName, gPrice, gImg) VALUES "
    sql_data = []

    idx, turn = 1, 1
    for idx, data in enumerate(datas):
        if (idx+1) % 100 == 0:
            sql.execute(sql_query + ", ".join(sql_data) + ";")
            sql_conn.commit()
            sql_data = []
            
        sql_value = "("
        sql_value += ",".join([ f'"{x}"' for x in data ])
        sql_value += ")"

        sql_data.append(sql_value)

    if len(sql_data) > 0:
        sql_query += ", ".join(sql_data) + ";"
        sql.execute(sql_query)
        sql_conn.commit()
    
    sql_conn.close()

run()
print(f"crawling end - {datetime.now()}")

# crontab -e > 0 19 * * * <python_path> <source_code_path>