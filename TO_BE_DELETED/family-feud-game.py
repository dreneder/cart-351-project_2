#Importing and setting up the python document
from flask import Flask, render_template, Response, request, jsonify
import json
import os

# --- MongoDB additions ---
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()
# --- end MongoDB additions ---

app = Flask(__name__)

# --- MongoDB config (kept exactly as discussed) ---
db_user = os.getenv("MONGODB_USER")
db_pass = quote_plus(os.getenv("DATABASE_PASSWORD"))
db_name = os.getenv("DATABASE_NAME")

app.config["MONGO_URI"] = (
     f"mongodb+srv://{db_user}:{db_pass}@cluster0.6ifd1w5.mongodb.net/{db_name}"
     "?retryWrites=true&w=majority&authSource=admin"
)

mongo = PyMongo(app)
# --- end MongoDB config ---

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

     # --- MongoDB collection ---
     collection = mongo.db.project2

     def upsert_response(question_key, response_text):
          #BUT, before we can use this data, we have to make sure the user data conforms to our 1-word requirement
          #We can do this by checking if each string is alphanumeric (isalnum()) - if not, we switch string to empty
          if not response_text.isalnum():
               return ""

          existing = collection.find_one({
               "Question": question_key,
               "Response": response_text
          })

          #If the string is valid, we add it to the server - either by appending it to the list of dictionaries or by incrementing the count of an existing response
          if existing:
               collection.update_one(
                    {"_id": existing["_id"]},
                    {"$inc": {"Count": 1}}
               )
          else:
               collection.insert_one({
                    "Question": question_key,
                    "Response": response_text,
                    "Count": 1
               })

          return response_text

     q_1Data = upsert_response("q1", q_1Data)
     q_2Data = upsert_response("q2", q_2Data)
     q_3Data = upsert_response("q3", q_3Data)

     # --- Legacy JSON file logic (commented out, preserved) ---
     """
     with open(file_path, "r") as dataFile:
          try:
               current_data = json.load(dataFile)
          except json.JSONDecodeError:
               current_data = []

     if (not (q_1Data.isalnum())):
         q_1Data = ""
     else:
          repeat = False
          for entry in current_data:
               if entry["Question"] == "q1" and entry["Response"] == q_1Data:
                    repeat = True
                    entry["Count"] += 1
                    break
          if (not repeat):
               current_data.append({"Question": "q1", "Response": q_1Data, "Count": 1})

     if (not (q_2Data.isalnum())):
         q_2Data = ""
     else:
          repeat = False
          for entry in current_data:
               if entry["Question"] == "q2" and entry["Response"] == q_2Data:
                    repeat = True
                    entry["Count"] += 1
                    break
          if (not repeat):
               current_data.append({"Question": "q2", "Response": q_2Data, "Count": 1})

     if (not (q_3Data.isalnum())):
         q_3Data = ""
     else:
          repeat = False
          for entry in current_data:
               if entry["Question"] == "q3" and entry["Response"] == q_3Data:
                    repeat = True
                    entry["Count"] += 1
                    break
          if (not repeat):
               current_data.append({"Question": "q3", "Response": q_3Data, "Count": 1})

     with open(file_path, "w") as dataFile:
          json.dump(current_data, dataFile, indent = 4)
     """
     # --- end legacy JSON logic ---

     #Seperate from any server/file code. This simply returns the data from the FETCH request
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
    #             payload = json.load(data_file)
    #         except json.JSONDecodeError:
    #             payload = []

    collection = mongo.db.project2
    payload = list(collection.find({}, {"_id": 0}))

    return Response(json.dumps(payload), mimetype="application/json")  # raw JSON response for fetch()


#Running the application
app.run(debug=True)
