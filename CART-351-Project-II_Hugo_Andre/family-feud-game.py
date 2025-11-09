#Importing and setting up the python document
from flask import Flask, render_template, request
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

#The game page route
@app.route("/game")
def game():
     return render_template("game.html")

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

#Running the application
app.run(debug=True)
