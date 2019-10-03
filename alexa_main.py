from flask import Flask,jsonify,request
from flask_ask import Ask, statement, question, session
import json
import requests
import time
import unidecode
import random
import time
import pika
from flask_socketio import SocketIO, send


app = Flask(__name__)
ask = Ask(app, "/")
socketio = SocketIO(app)

laptop_dict = dict()
backend_url = "http://localhost:5001/api/search/alexa"

# This is taken from the synonyms stated in the attribute area in alexa model
attributes_dict = {
"price" : ['price'],"processorCount" :['processor count','processorcount','cores','processor cores'],'ram':['ram'],'processorSpeed':['processorspeed','processor speed','processor','speed'],
'displayResolutionSize': ['resolution'], 'screenSize' : ['screen','display','size','screen size'],'hdd':['drive','hard drive','memory']
}


@socketio.on('connect')
def test_connect():
    print("Connected")

#First inovcation
@ask.launch
def start_skill():
    welcome_message = get_random_hello_message()
    return question(welcome_message)



@ask.intent("more", mapping={"value": "attribute"})
def get_more(value):

    value = get_camelCase_attribute(value)
    #If the laptop attributes are already set from front end.

    if len(laptop_dict.keys()) > 0  :
        laptop_dict.update({"intent":"more"})
        laptop_dict.update({"intentVariable":value})
        intent_variable = laptop_dict["intentVariable"]

        query_result = get_query_result_from_backend()
        #In case the result has any loose shit in it.

        try :
            message = get_random_result_success_message(intent_variable,query_result)
            send_query_result_to_frontend(query_result)
        except :
            message = get_random_fail_message()
    else : #Fail message
        message = get_random_no_chosen_laptop_fail_message()

    return statement(message)

@ask.intent("less", mapping={"value": "attribute"})
def get_less(value):

    value = get_camelCase_attribute(value)

    #If the laptop attributes are already set from front end.
    if len(laptop_dict.keys()) > 0 :
        #TODO : refine the name of attributes to match backend. IMPORTANT!!!!!!!
        laptop_dict.update({"intent":"less"})
        laptop_dict.update({"intentVariable":value})

        intent_variable = laptop_dict["intentVariable"]

        query_result = get_query_result_from_backend()
        try :
            message = get_random_result_success_message(intent_variable,query_result)
            send_query_result_to_frontend(query_result)
        except :
            message = get_random_fail_message()
    else : #Fail message
        message = get_random_no_chosen_laptop_fail_message()

    return statement(message)



#Sets attributes for the laptop
@app.route('/alexa/setter', methods=['POST'])
def set_laptop_attributes():

    print("Setting Laptop attributes ..")

    data = request.get_json()

    laptop_dict.clear()

    laptop_dict.update(data)

    return jsonify(laptop_dict)

def get_query_result_from_backend():

    print("Getting result from backend..")

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    req = requests.post(backend_url,data = json.dumps(laptop_dict),headers = headers )


    response = req.json()

    laptop_dict.clear()

    return response

def send_query_result_to_frontend(query_result):
    #TODO: send query_result
    socketio.emit('result', query_result)
    laptop_dict.clear()

    pass

def get_random_hello_message():

    messages = ["Hello! What would you like to do?"
    ,"Hey there, ready to shop for some laptops?"
    ,"I am here, tell me what you need"
    ,"Alexa is ready for some action, are you?"]

    random_response = random.sample(messages,1)

    return random_response[0]

def get_random_no_chosen_laptop_fail_message():

    messages = ["You seem to have forgotten to choose a laptop, please choose one first"
    ,"You have to choose a laptop first to be able to criticize it",
    "I am sorry I couldn't find any chosen laptop"
    ,"Did you choose a laptop?"
    ,"Hey there, ready to shop for some laptops?"
    ,"I am here, tell me what you need"
    ,"Alexa is ready for some action, are you?"]

    random_response = random.sample(messages,1)

    return random_response[0]

def get_random_fail_message():

    #To feel more human like.
    messages = ["I seem to have encountered a problem with Laptopshop, please try again"
    ,"There seems to be a problem, could you try again?",
    "There was a problem with your request, please try again later"]

    random_response = random.sample(messages,1)

    return random_response[0]

def get_random_result_success_message(intent_variable,query_result):
    message = "I found this laptop that I think you will like, its "+intent_variable+" is "+str(query_result[0][intent_variable])

    #To feel more human like.
    messages = ["I found a laptop that I think you will like, "
    ,"How about this laptop, ",
    "Here is the laptop I found for you, "
    ,"Christmas is here, I just found the perfect laptop for you, "]

    random_response = random.sample(messages,1)

    brand_name = str(query_result[0]["brandName"])
    price = str(query_result[0]["price"])

    message = str(random_response[0])+" it is "+brand_name+" which costs "+price+"euros , also its "+intent_variable+" is "+str(query_result[0][intent_variable])


    return message

def get_camelCase_attribute(attribute_name):
    print(attribute_name)
    for attribute in attributes_dict :
        if attribute_name.lower() in attributes_dict[attribute]:
            return attribute



if __name__ == "__main__":
    socketio.run(app,port = 5004)
