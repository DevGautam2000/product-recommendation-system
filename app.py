"""
        AUTHOR: GAUTAM CHANDRA SAHA
        DATE & TIME: 13/01/22 AT 5:09 PM ON Thu
"""

import json
from bson import json_util
from bson.objectid import ObjectId
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import db
import pymongo
import pandas as pd

app = Flask(__name__)
app.json_encoder = db.MongoJSONEncoder
app.url_map.converters['ObjectId'] = db.ObjectIdConverter
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

client = pymongo.MongoClient("mongodb://127.0.0.1:27017")

port = 6050


def fetch(id):

    # Database Name
    db = client["foodon"]
    col = db["orders"]

    objInstance = ObjectId(id)

    docs = col.find_one({"user": objInstance})

    # print(docs)

    data = []
    data.append(json.dumps(docs, indent=4, default=json_util.default))

    return data


def main():

    @app.route('/recommend/<string:id>', methods=['POST'])
    def post(id):
        obj = fetch(id)
        docs = json.loads(obj[0])
        prods = []
        for item in docs['orderedItems']:
            # print(f"{item=}")
            for products in item['product']:
                prods.append(products)
        # print(f"{prods=}")
        _json = open("names.json", 'w')
        _json.write(json.dumps(prods))
        _json.close()

        with open('names.json', encoding='utf-8') as inputfile:
            df = pd.read_json(inputfile)

        df.to_csv('prods.csv', encoding='utf-8', index=False)

        fileObject = open("./names.json", "r")
        jsonContent = fileObject.read()
        prods_list = json.loads(jsonContent)

        names = [item['name'] for item in prods_list]

        from random import randrange as random

        import recommendation_sys as recommender
        recom = recommender.recommend(names[random(len(names))])
        final_recom = []
        for item in recom:
            for lobj in prods_list:
                if item == lobj['name']:
                    final_recom.append(lobj)

        # print(f"{final_recom=}")

        return jsonify(final_recom)

    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(port=port)


if __name__ == "__main__":
    main()
