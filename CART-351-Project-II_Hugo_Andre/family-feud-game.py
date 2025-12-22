#Importing and setting up the python document
from flask import Flask, render_template, Response, request, jsonify, session
from flask_pymongo import PyMongo
import json
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret")

db_user = os.getenv("MONGODB_USER")
db_pass = os.getenv("DATABASE_PASSWORD")
db_name = os.getenv("DATABASE_NAME")
app.config["MONGO_URI"] = (
     f"mongodb+srv://{db_user}:{db_pass}@cluster0.6ifd1w5.mongodb.net/{db_name}?retryWrites=true&w=majority"
)
mongo = PyMongo(app)

UPLOAD_FOLDER = 'static/uploads' 

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB limit

#The default route
@app.route("/")
def home():
      return render_template("home.html")

#The survey page route
@app.route("/survey")
def survey():
     return render_template("survey.html")

@app.route("/getDataFromForm")
def getDataFromForm():

     #GET Requests are stored in request.args
     app.logger.info(request.args)

     #Now we want to store the user data from the survey in variables q_1Data, q_2Data, q_3Data
     #We also want to .strip() leading or trailing whitespaces
     q_1Data = request.args["q_1"].strip().upper()
     q_2Data = request.args["q_2"].strip().upper()
     q_3Data = request.args["q_3"].strip().upper()

     # file_path = os.path.join("files", "data.json")
     # with open(file_path, "r") as dataFile:
     #      try:
     #           current_data = json.load(dataFile)
     #      except json.JSONDecodeError:
     #           current_data = []

     collection = mongo.db.project2  # switching persistence from JSON file to MongoDB collection

     def upsert_response(question_key, response_text):
          """Validate, then insert or increment a response in Mongo."""
          if not response_text.isalnum():
               return ""
          existing = collection.find_one({"Question": question_key, "Response": response_text})
          if existing:
               collection.update_one({"_id": existing["_id"]}, {"$inc": {"Count": 1}})
          else:
               collection.insert_one({"Question": question_key, "Response": response_text, "Count": 1})
          return response_text

     q_1Data = upsert_response("q1", q_1Data)
     q_2Data = upsert_response("q2", q_2Data)
     q_3Data = upsert_response("q3", q_3Data)

     # Legacy JSON file approach (kept for reference, now replaced by MongoDB)
     # file_path = os.path.join("files", "data.json")
     # with open(file_path, "r") as dataFile:
     #      try:
     #           current_data = json.load(dataFile)
     #      except json.JSONDecodeError:
     #           current_data = []
     #
     # if (not (q_1Data.isalnum())):
     #     q_1Data = ""
     # else:
     #      repeat = False
     #      for entry in current_data:
     #           if entry["Question"] == "q1" and entry["Response"] == q_1Data:
     #                repeat = True
     #                entry["Count"] += 1
     #                break
     #      if (not repeat):
     #           current_data.append({"Question": "q1", "Response": q_1Data, "Count": 1})
     #
     # if (not (q_2Data.isalnum())):
     #     q_2Data = ""
     # else:
     #      repeat = False
     #      for entry in current_data:
     #           if entry["Question"] == "q2" and entry["Response"] == q_2Data:
     #                repeat = True
     #                entry["Count"] += 1
     #                break
     #      if (not repeat):
     #           current_data.append({"Question": "q2", "Response": q_2Data, "Count": 1})
     #
     # if (not (q_3Data.isalnum())):
     #     q_3Data = ""
     # else:
     #      repeat = False
     #      for entry in current_data:
     #           if entry["Question"] == "q3" and entry["Response"] == q_3Data:
     #                repeat = True
     #                entry["Count"] += 1
     #                break
     #      if (not repeat):
     #           current_data.append({"Question": "q3", "Response": q_3Data, "Count": 1})
     #
     # with open(file_path, "w") as dataFile:
     #      json.dump(current_data, dataFile, indent = 4)

     # with open(file_path, "w") as dataFile:
     #      json.dump(current_data, dataFile, indent = 4)

     return ({"data_received": "success", "q_1": q_1Data, "q_2": q_2Data, "q_3": q_3Data})


#The game page route
@app.route("/game")
def game():

    # initially the processig was going to be done in python, I will leave this code here for documentation purposes
     # # this function creates a list 
     # def populate_grid(data, question, grid_size=4):
     #      responses = [item for item in data if item.get("Question") == question]

     #      #  this will obtain the highest count of an item
     #      def get_count(item):
     #           return item["Count"]

     #      responses.sort(key=get_count, reverse=True)

     #      grid = []
     #      for i in range(grid_size):
     #           if i < len(responses):
     #                grid.append(responses[i]["Response"])
     #           else:
     #                grid.append(None)
     #      return grid
     
     return render_template("game.html")


# Lightweight API endpoint so the front-end can fetch the latest survey data
@app.route("/getDataFromGame")
def game_data():
    # file_path = os.path.join("files", "data.json")
    # if not os.path.exists(file_path):
    #     payload = []
    # else:
    #     with open(file_path, "r") as data_file:
    #         try:
    #             payload = json.load(data_file)  # stored as list[dict]
    #         except json.JSONDecodeError:
    #             payload = []

    collection = mongo.db.project2
    payload = list(collection.find({}, {"_id": 0}))  # omit Mongo _id to mirror old JSON shape

    # Legacy JSON file approach (kept for reference, now replaced by MongoDB)
    # file_path = os.path.join("files", "data.json")
    # if not os.path.exists(file_path):
    #     payload = []
    # else:
    #     with open(file_path, "r") as data_file:
    #         try:
    #             payload = json.load(data_file)  # stored as list[dict]
    #         except json.JSONDecodeError:
    #             payload = []

    return Response(json.dumps(payload), mimetype="application/json")  # raw JSON response for fetch()

#Running the application
app.run(debug=True)
