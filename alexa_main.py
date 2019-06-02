from flask import Flask,jsonify,request
from flask_ask import Ask, statement, question, session
import json
import requests
import time
import unidecode
import random

app = Flask(__name__)
ask = Ask(app, "/")

laptop_dict = dict()
query_result = list()
backend_url = "http://localhost:5001/api/search/alexa"

#First inovcation
@ask.launch
def start_skill():
    welcome_message = get_random_hello_message()
    return question(welcome_message)

def get_random_hello_message():

    messages = ["Hello! What would you like to do?"
    ,"Hey there, ready to shop for some laptops?"
    ,"I am here, tell me what you need"
    ,"Alexa is ready for some action, are you?"]

    random_response = random.sample(messages,1)

    return random_response[0]

@ask.intent("more", mapping={"value": "attribute"})
def get_more(value):
    #If the laptop attributes are already set from front end.
    if len(laptop_dict.keys()) > 0 :

        #TODO : refine the name of attributes to match backend. IMPORTANT!!!!!!!

        laptop_dict.update({"intent":"more"})
        laptop_dict.update({"intentVariable":value})

        query_result.append(get_query_result())
        #In case the result has any loose shit in it.
        try :
            message = "I found this laptop that I think you will like, its "+laptop_dict["intentVariable"]+" is "+str(query_result[0][0][laptop_dict["intentVariable"]])
        except :
            message = get_random_fail_message()
    else : #Fail message
        message = get_random_fail_message()

    return statement(message)

@ask.intent("less", mapping={"value": "attribute"})
def get_less(value):

    #If the laptop attributes are already set from front end.
    if len(laptop_dict.keys()) > 0 :

        #TODO : refine the name of attributes to match backend. IMPORTANT!!!!!!!

        laptop_dict.update({"intent":"less"})
        laptop_dict.update({"intentVariable":value})

        query_result.append(get_query_result())
        print(query_result)
        #In case the result has any loose shit in it.
        try :
            message = "I found this laptop that I think you will like, its "+laptop_dict["intentVariable"]+" is "+str(query_result[0][0][laptop_dict["intentVariable"]])
        except :
            message = get_random_fail_message()
    else : #Fail message
        message = get_random_fail_message()

    return statement(message)

def get_random_fail_message():

    #To feel more human like.
    messages = ["I am sorry I couldn't find any chosen laptop"
    ,"You seem to have forgotten to choose a laptop, please choose one first"
    ,"You have to choose a laptop first to be able to criticize it"]

    random_response = random.sample(messages,1)

    return random_response[0]

#Sets attributes for the laptop
@app.route('/alexa/setter', methods=['POST'])
def set_laptop_attributes():

    data = request.get_json()

    laptop_dict.update(data)

    return jsonify(laptop_dict)


@app.route('/alexa/getQuery',methods = ['POST'])
def return_query_to_frontend():
    #The query has already been processed.
    if len(query_result) > 0 :
    #print(response)
        json_response = jsonify(query_result)
        # reset the query_result variable.
        query_result.clear()

        laptop_dict.clear()
    else :#Fail, result is not here yet, keep listening.
        json_response = ""

    return json_response

def get_query_result():

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    req = requests.post(backend_url,data = json.dumps(laptop_dict),headers = headers )

    response = req.json()

    return response

if __name__ == "__main__":
     app.run(debug=True)
