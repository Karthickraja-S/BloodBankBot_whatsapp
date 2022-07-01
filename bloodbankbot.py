from turtle import Turtle
from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)


@app.route('/bot', methods=['POST']) 

def bot():

    def getdatabase():
        from pymongo import MongoClient
        import pymongo
        connection_string = "mongodb+srv://karthi:karthi1412@cluster0.grst1.mongodb.net/bloodvolunteers?retryWrites=true&w=majority"
        client = MongoClient(connection_string)
        return client['bloodvolunteers']

    def insert(details):
        dbname = getdatabase()
        collection_name = dbname["volunteer_details"]      # the collection name is volunteer_details
        insertdata={
            "Name":details[1],
            "Mobile Number":details[2],
            "Location":details[3],
            "Blood Group":details[4],
            "Status":"Active"
        }
        collection_name.insert_one(insertdata)

    def searchdetails(det):
        dbname = getdatabase()
        collection_name = dbname["volunteer_details"]
        bloodgroup = det[1]
        location = det[2]
        item_details = collection_name.find()
        ans=""
        for item in item_details:
            if(item['Blood Group'].lower()==bloodgroup and item['Location'].lower()==location and item['Status']=="Active"):
                #print("Person name = ",item['Name']," Mobile Number : ",item['Mobile Number'])
                dett = "\n"+"Person name = "+item['Name']+"\n"+" Mobile Number : "+item['Mobile Number']
                ans = ans+dett+"\n"
        return ans

    def delete_details(details):
        dbname = getdatabase()
        collection_name = dbname["volunteer_details"]      # the collection name is volunteer_details
        myquery = { "Mobile Number": details[1] }
        collection_name.delete_one(myquery)

    def checkthenumberispresentornot(n):
        dbname = getdatabase()
        collection_name = dbname["volunteer_details"]
        item_details = collection_name.find()
        for item in item_details:
            if (item["Mobile Number"]==n):
                return True
        return False

    resp = MessagingResponse()
    msg = resp.message()    
    
    responded = False
    incoming_msg = request.values.get('Body', '').lower()
    # 1->make volunteer 2->searching data
    if '1' in incoming_msg:         # he will provide 1,karthick,7418386415,theni,B+
        s = incoming_msg.split(",")
        if(len(s)==5):
            msg.body("Inserting details....\n")
            insert(s)
            msg.body("\nCongrats.. You are now a volunteer to donate blood .")
            responded = True
        else:
            msg.body("Error. for your reference please see below example\n1,karthi,9999999999,theni,b+\n1,suriya,7777777777,madurai,B+")
            responded=True
    elif '2' in incoming_msg:
        s = incoming_msg.split(",")      #he will give like 2,b+,theni
        if(len(s)==3):
            details_fetched = searchdetails(s)
            if(details_fetched!=""):
                msg.body(details_fetched)
                responded=True
            else:
                msg.body("Sorry No details Found.. Try with nearby location.")
                responded=True
        else:
            msg.body("Invalid input. for your reference please see below example\n2,b+,madurai\n2,o+,theni")
            responded=True
    elif '3' in incoming_msg:     #3,mobilenumber
        s=incoming_msg.split(",")
        if(len(s)==2):
            if(checkthenumberispresentornot(s[1])):
                #delete the record
                delete_details(s)
                msg.body("Deleted Sucessfully . Hope you will soon be a blood volunteer. Take care !")
            else:
                msg.body("The number is not is in volunteer list . Cant able to delete.")
            responded = True
        else:
            msg.body("Invalid input. for your reference please see below example\n3,9999999999\n3,7878786545")
            responded=True
    if 'menu' in incoming_msg:
        torespond="Hi Dear.The mode available are \n1-insert 2-search 3-delete details ..\nExamples given below\nFor insert : 1,[yourname],[mobilenumber],[location],[bloodgroup]\nFor search : 2,[bloodgroup],[location]\nFor delete : 3,[mobilenumber]"
        msg.body(torespond)
        responded=True
    if not responded:
        msg.body("Please type menu to initialise chatbot. ")
    return str(resp)


if __name__ == '__main__':
    app.run()