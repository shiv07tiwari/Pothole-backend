from flask import Flask, request, jsonify
import json
from pymongo import MongoClient
import flask
from bson import json_util
from bson.objectid import ObjectId

LATITUDE = 'latitude'
LONGITUDE = 'longitude'
COUNTER = 'counter'


app = Flask(__name__)

client = MongoClient()
db = client['pymongo_test']

def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

# Testing route
@app.route("/<name>")
def home(name):
    posts = db.posts
    posts.remove()
    return "Hello user " + name

def addToMainDatabase(pothole_entry, posts):
    posts.insert_one(pothole_entry)
    
def increaseCounterMainDatabase(pothole_entry, posts, counter):
    counter = int(counter) + 1    
    posts.update_one(
        {LATITUDE:pothole_entry[LATITUDE],LONGITUDE:pothole_entry[LONGITUDE]},
        { "$set": {
            COUNTER:str(counter)
        }}
    )
    
# Access database to add a new pothole or inc the counter if it already exists
@app.route('/pothole', methods = ['POST'])
def savePotholetoDatabase() :
    if (request.is_json):
        json_data = request.get_json()
        #print(type(json_data))
        json_string = json.dumps(json_data)
        #print(type(json_string))
        parsed_json = (json.loads(json_string))
        #print(type(parsed_json['data']))
        for x in parsed_json['data']:
            print(type(x))
            print(x)

        posts = db.posts
        for x in parsed_json['data']:
            bills_post = posts.find({LATITUDE:x[LATITUDE],
             LONGITUDE:x[LONGITUDE]})
            if (bills_post.count() > 0):
                for bill in bills_post:
                    a = bill[COUNTER]
                    #print("Counter", a)
                print("Updating database")
                increaseCounterMainDatabase(x,posts,a)
            else:
                print("Adding to database")
                addToMainDatabase(x, posts)
            
        req = request.json
        print(req)
        return "Thanks"

# Access database to get active potholes
@app.route('/potholes',methods = ['GET'])
def getPotholes():
    
    latitude = request.args.get('lat')
    longitude = request.args.get('lon')
    counter = request.args.get('count')
    print("FINAL : ",latitude,longitude,counter)

    posts = db.posts

    if (latitude == None and longitude == None and counter == None):
         bills_post = list(posts.find())
    elif (latitude != None and longitude != None):
         bills_post = list(posts.find({LATITUDE:latitude, LONGITUDE:longitude}))
    else:
        return "Invalid request"
    for x in bills_post:
        print(type(x))
        print(x)
    res = json.dumps(bills_post, default=json_util.default)

    return res

# Get an individual pothole based on it's id
@app.route('/pothole/<id>',methods=['GET'])
def getPothole(id):
    print("Type 1 ",type(id))
    
    posts = db.posts
    pothole_details = posts.find({"_id" : ObjectId(id)})
    for x in pothole_details:
        res = json.dumps(x, default=json_util.default)

    return res


if __name__ == "__main__":
    app.run(debug=True, port=5000)