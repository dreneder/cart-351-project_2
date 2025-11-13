#Importing and setting up the python document
from flask import Flask, render_template, Response, request, jsonify
import json
import os

app = Flask(__name__)

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

     file_path = os.path.join("files", "data.json")

     #For accessing server data to handle adding new responses
     with open(file_path, "r") as dataFile:

          #Each response is stored in the server as a dictionary (q#, response, count)
          #current_data is a list of existing dictionaries
          #We use try/catch because the data can't parse an empty file, so we initialize the data to []
          try:
               current_data = json.load(dataFile)

          except json.JSONDecodeError:
               current_data = []

     #BUT, before we can use this data, we have to make sure the user data conforms to our 1-word requirement
     #We can do this by checking if each string is alphanumeric (isalnum()) - if not, we switch string to empty
     if (not (q_1Data.isalnum())):
         q_1Data = ""

     #If the string is valid, we add it to the server - either by appending it to the list of dictionaries or by incrementing the count of an existing response
     else:
     
          #Checking all existing responses - if there's a matching response for the current question, increment the count
          repeat = False
          for entry in current_data:

               if entry["Question"] == "q1" and entry["Response"] == q_1Data:
                    repeat = True
                    entry["Count"] += 1
                    break
     
          #If there is no existing response, add it to the list of dictionaries
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

     #Now that the current data in the file has been altered by each response by either appending dictionaries or changing counts...
     #We can simply rewrite the file by dumping the new altered data
     with open(file_path, "w") as dataFile:
          json.dump(current_data, dataFile, indent = 4)

     #Seperate from any server/file code. This simply returns the data from the FETCH request
     return ({"data_received": "success", "q_1": q_1Data, "q_2": q_2Data, "q_3": q_3Data})


#The game page route
@app.route("/game")
def game():

     # this function creates a list 
     def populate_grid(data, question, grid_size=4):
          responses = [item for item in data if item.get("Question") == question]

          #  this will obtain the highest count of an item
          def get_count(item):
               return item["Count"]

          responses.sort(key=get_count, reverse=True)

          grid = []
          for i in range(grid_size):
               if i < len(responses):
                    grid.append(responses[i]["Response"])
               else:
                    grid.append(None)
          return grid
     
     
     # Questions dict is passed to the template so JS knows the prompt for each qStage
     questions = {
          "question0": "What is the first item you use after waking up in the morning?",
          "question1": "Which day of the week is most fitting for filing your taxes?",
          "question2": "Name a country you would most like to visit",
     }

     return render_template("game.html", questions=questions)


# Lightweight API endpoint so the front-end can fetch the latest survey data
@app.route("/getDataFromGame")
def game_data():
    file_path = os.path.join("files", "data.json")
    if not os.path.exists(file_path):
        payload = []
    else:
        with open(file_path, "r") as data_file:
            try:
                payload = json.load(data_file)  # stored as list[dict]
            except json.JSONDecodeError:
                payload = []

    return Response(json.dumps(payload), mimetype="application/json")  # raw JSON response for fetch()

#Running the application
app.run(debug=True)
