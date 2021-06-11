from flask import Flask, request
from json import dumps
from psycopg2 import connect
from os import getenv
from functools import cache


PAGE_SIZE = 25


app = Flask(__name__)
conn = connect(dbname=getenv("DBNAME"), user=getenv("DBUSER"),
               password=getenv("DBPASS"), host=getenv("DBHOST"))


@cache
def get_sectors():
    cur = conn.cursor()
    cur.execute("SELECT nombre from sectores;")
    return cur.fetchall()


@cache
def get_regions():
    cur = conn.cursor()
    cur.execute("SELECT nombre FROM regiones;")
    return cur.fetchall()


def process_search(text: str):
    print(text.split())


def process_get(data: dict):
    offset = PAGE_SIZE * (data.get("page", 1) - 1)
    from_year = data.get("from", 1900)
    till_year = data.get("until", 2100)
    sector = tuple(data.get("sector", get_sectors()))
    region = tuple(data.get("region", get_regions()))
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM conflictos " +
        "WHERE year BETWEEN %s AND %s AND region IN %s AND sector IN %s " +
        "OFFSET %s ROWS FETCH FIRST %s ROWS ONLY;",
        (from_year, till_year, region, sector, offset, PAGE_SIZE)
    )
    return dumps(cur.fetchall())


@app.route("/api/search", methods=["GET"])
def search():
    text = request.args.get("text")
    process_search(text)
    return "OK"


@app.route("/api/get", methods=["GET"])
def get():
    data = request.json
    payload = process_get(data)
    return payload
