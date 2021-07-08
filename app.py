# TODO page in search
from flask import Flask, request, jsonify
from json import dumps
from psycopg2 import connect
from os import getenv
from functools import cache
from elasticsearch import Elasticsearch
from flask_cors import CORS

PAGE_SIZE = 10


app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
conn = connect(dbname=getenv("DBNAME"), user=getenv("DBUSER"),
               password=getenv("DBPASS"), host=getenv("DBHOST"))
es = Elasticsearch([{"host": getenv("ESHOST"), "port": getenv("ESPORT")}])


@cache
def get_sectors():
    cur = conn.cursor()
    cur.execute("SELECT nombre from sectores;")
    data = cur.fetchall()
    cur.close()
    return data


@cache
def get_regions():
    cur = conn.cursor()
    cur.execute("SELECT nombre FROM regiones;")
    data = cur.fetchall()
    cur.close()
    return data


def process_search(text: str, page: int):
    res = es.search(index="files", body={
        "from": PAGE_SIZE * (page - 1),
        "size": PAGE_SIZE,
        "query": {
            "match": {
                "attachment.content": {
                    "query": text
                }
            }
        },
        "fields": [
            "filename"
        ],
        "_source": False
    })
    filenames = []
    print(res)
    for hit in res["hits"]["hits"]:
        filenames.append(hit["fields"]["filename"][0])
    if not filenames:
        return {}
    filenames = tuple(filenames)
    cur = conn.cursor()
    cur.execute("SELECT filename, name, region, sector, year, content FROM conflictos " +
                "WHERE filename IN %s;", (filenames, ))
    data = dumps(cur.fetchall())
    cur.close()
    return data


def process_get(data: dict):
    offset = PAGE_SIZE * (data.get("page", 1) - 1)
    from_year = data.get("from", 1900)
    till_year = data.get("until", 2100)
    sector = tuple(data.get("sector", get_sectors()))
    region = tuple(data.get("region", get_regions()))
    cur = conn.cursor()
    cur.execute(
        "SELECT filename, name, region, sector, year, content FROM conflictos " +
        "WHERE year BETWEEN %s AND %s AND region IN %s AND sector IN %s " +
        "OFFSET %s ROWS FETCH FIRST %s ROWS ONLY;",
        (from_year, till_year, region, sector, offset, PAGE_SIZE)
    )
    data = dumps(cur.fetchall())
    cur.close()
    return data


@app.route("/api/search", methods=["GET"])
def search():
    text = request.args.get("text")
    page = request.args.get("page", type=int)
    page = 1 if page is None else page
    payload = process_search(text, page)
    return payload


@app.route("/api/get", methods=["POST"])
def get():
    print("Entre")
    data = request.json
    payload = process_get(data)
    return payload


@app.route("/api/filters", methods=["GET"])
def filters():
    regions = get_regions()
    sectors = get_sectors()
    return jsonify({"regiones": regions, "sectores": sectors})
