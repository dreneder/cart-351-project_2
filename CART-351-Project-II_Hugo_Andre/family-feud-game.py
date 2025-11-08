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

     #BUT, before we can use this data, we have to make sure the user data conforms to our 1-word requirement
     #We can do this by checking if each string is alphanumeric (isalnum()) - if not, we switch string to empty
     if (not (q_1Data.isalnum())):
         q_1Data = ""

     if (not (q_2Data.isalnum())):
         q_2Data = ""

     if (not (q_3Data.isalnum())):
         q_3Data = ""

     return ({"data_received": "success", "q_1": q_1Data, "q_2": q_2Data, "q_3": q_3Data})

#       #recieving data from fetch request
#       data = request.get_json() 
#       print("Recieved data: ", data)
     
#      #parsing data from the request json object
#       color = data.get("color")
#       print ("color recieved:", color)

#       #file path for reading and writing from files
#       file_path = os.path.join("files", "data.txt")

#       #because we want to identify if the picked color already exists in the server, we loop through the server file and count
#       count = 0
#       with open(file_path, "r") as f:
#           for line in f:
               
#                text = line.strip()

#                if color in text:
#                     count +=1

#       #if that exact color was picked, then notify user. If not, notify user
#       if (count < 1):
#             message = "No other user has picked this colour!"

#       else:
#            message = f"This colour has been picked {count} time(s)!"

#       #finally, after looping through all the exisitng colors, we can write this one to the file
#       with open(file_path, "a") as f:
#           f.write(color + "\n")

#       app.logger.info(request.form)

#       #Returning the data
#       return jsonify({"data_received":"yes", "color":color, "message":message})

#Running the application
app.run(debug=True)
