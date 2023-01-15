#!/usr/bin/python3
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OSU ID: <zhang.11041>
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# listServer -- initial shoooping lists are located here 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
import socket
import sys
import json
import logging
from configparser import ConfigParser
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Variables
#···············································································
serverIP='127.0.0.1'                       # loopback address (localhost)  
serverPort = 12000
serverAddress = (serverIP, serverPort)
processingClientRequests=True              # Flag for processing
g_file = 'groceries.json'		   # the groceires json.file as the database of shopping lists
serverResponse = ""
serverResponse1 = ""
processingEdit1 = True

#···············································································
# convert the json file into a list of dictionaries
def convert(f):
    with open(f) as json_file:
        data = json.load(json_file)
    return data
#···············································································
# convert the json file into a list of dictionaries
def convert(f):
    with open(f) as json_file:
        data = json.load(json_file)
    return data

# wirte the updated list into our groceries.json file
def write(ls):
    with open(g_file, 'w') as json_file:
        json.dump(ls, json_file)


# print the titles of all the dictionaries in the json file
def catalog(ls):
    i = 0
    result = "\nThere are the following titles of shopping lists in the database: \n"
    for d in ls:
        result += str(i)
        result += "."
        result += list(d.keys())[0]
        result += "\n"
        i=i+1
    return result

# add the new list (only the key) to the json file
def createNew(g_list, newDict):
    g_list.append({newDict: []})
    write(g_list)

# print dictionary #num in the json file
def display(g_list, num):
    result = "\nThe content in list " + str(num) + " is as follows: \n"
    result += str(g_list[num])
    return result

# delete a list (represented by a dictionary) from the json file
def delete(num, g_list):
    g_list.pop(num)
    write(g_list)

# add an item into a list (represented by dictionary)
def add(string, g_list, d, num):
    # get the only key(title) from the dictionary
    key = list(d.keys())[0]
    item_list = d.get(key)
    item_list.append(string)
    #update g_list
    d[key] = item_list
    g_list[num] = d
    write(g_list)

# remove an item from the list (represented by dictionary value)
def removeItem(d, item, g_list, num): 
    result = "item not in the list!"
    key = list(d.keys())[0]
    item_list = d.get(key)
    item_list.remove(item)
    result = item + "removed!"
    d[key] = item_list
    g_list[num] = d
    write(g_list)
    return result

def createLog():
    # create a logging file and specify its format
    logging.basicConfig(filename = 'list.log', format='%(asctime)s %(message)s', datefmt = '%a %b %d %l: %M:%S %Y', level = logging.INFO)


# print dictionary value of #num in the json file
def show(g_list, num, d):
    result = "\nThe content in list " + str(num) + " is as follows: \n"
    key = list(d.keys())[0]
    item_list = d.get(key)
    result += str(item_list)
    return result

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Application Main
#
def main():
    config = ConfigParser()
    config.read('config.ini')
    serverPort = int(config['default']['port'])
    serverAddress = (serverIP, serverPort)   
    # save the log file recording all the requests and responses
    createLog()
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # creates a welcoming TCP socket using Ipv4 as underlying network
    try:
        serverSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('echoTCPserver :: Opened TCP socket')
        print('echoTCPserver :: Server starting on ',serverIP)
        processingClientRequests=True

        try:    
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
            # server binds to a port through the welcoming socket(server socket)
            #
            serverSocket.bind(serverAddress)
            print('echoTCPserver :: Bound to port ',serverPort)
            processingClientRequests=True
        except:
            print('echoTCPserver :: Unable to bind to port '+str(serverPort))
            processingClientRequests=False

    except:
        print('echoTCPserver :: Unable to create a server socket')
        processingClientRequests=False

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Continue if socket opened and bound to a port
    #
    if processingClientRequests:

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # welcoming socket begins listening for a client
        #
        print('echoTCPserver :: Listening on the server port')
        serverSocket.listen()
        logging.info('starting on port %s', serverPort)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # creates a new socket dedicated to the particular client upon receiving the client's request
        #
        clientConnection,clientAddress=serverSocket.accept()
        print('echoTCPserver :: Accepted connection from ',str(clientAddress))

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Process client requests
        #
        while processingClientRequests:
	    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            processingEdit1 = True	    
            # Wait for a client request, max request is 2K
            
            clientRequest=clientConnection.recv(2048).decode()
	    # default server repsonse for all invalid commands
            print('echoTCPserver :: Client request received: ',clientRequest)
            lastChar = clientRequest[-1:]
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            g_list = convert(g_file)
            length = len(g_list)

            # Check if client wants to close
            #
            if clientRequest.upper() == 'EXIT':
                processingClientRequests=False
                logging.info('RESPONSE INFO %s the list sent', 'exit')

                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # operations on lists based on client's requests
            else:
                if clientRequest.upper() == 'CATALOG':
                    serverResponse = catalog(g_list)
                    logging.info('RESPONSE INFO %s the list sent', 'catalog')
                    print('echoTCPserver :: Sending server response ', serverResponse)
                    clientConnection.send(serverResponse.encode())

                elif clientRequest.startswith("display"):
                    num = int(lastChar)
                    serverResponse = display(g_list, num)
                    logging.info('RESPONSE INFO %s the list sent', 'display')
                    print('echoTCPserver :: Sending server response ', serverResponse)
                    clientConnection.send(serverResponse.encode())

                elif clientRequest.startswith("create"):
                    #clientRequest1=clientConnection.recv(2048).decode()
                    newList = clientRequest[7:len(clientRequest)]
                    createNew(g_list, newList)
                    serverResponse = "list " + newList + " created!\n"
                    logging.info('RESPONSE INFO %s new list sent', 'create')
                    print('echoTCPserver :: Sending server response ', serverResponse)
                    clientConnection.send(serverResponse.encode())

                elif clientRequest.startswith("delete"):
                    num = int(lastChar)
                    delete(num, g_list)
                    serverResponse = "list" + str(num) + " deleted!"
                    logging.info('RESPONSE INFO %s the list sent', 'delete')
                    print('echoTCPserver :: Sending server response ', serverResponse)
                    clientConnection.send(serverResponse.encode())

                elif clientRequest.startswith("edit"):
		    # lastChar is the #list to edit
                    lastChar = clientRequest[-1:]
                    print("you are editing list ", lastChar)
                    #editResponse = "you are editing list " + lastChar

                    logging.info('RESPONSE INFO %s the list sent', 'edit')

                    while processingEdit1:
                        num = int(lastChar)
                        #update the g_list:
                        g_list = convert(g_file)

                        # wait for the subrequest from the client
                        clientRequest1 = clientConnection.recv(2048).decode()
                        print('echoTCPserver :: Edit request received ', clientRequest1)
                        if clientRequest1 == 'quit':
                            processingEdit1 = False
                            serverResponse1 = "Quitting edit mode"

                        else:
                            if clientRequest1.startswith("show"):
                                index = int(lastChar)
                                d = g_list[index]
                                serverResponse1 = show(g_list, index, d)

                            elif clientRequest1.startswith("add"):
                                newItem = clientRequest1[4:len(clientRequest1)]
                                index = int(lastChar)
                                d = g_list[index]
                                add(newItem, g_list, d, index)
                                serverResponse1 = "item "+ newItem + " added!"
                            elif clientRequest1.startswith("remove"):
                                index = int(lastChar)
                                d = g_list[index]
                                item = clientRequest1[7:len(clientRequest1)]
                                serverResponse1 = removeItem(d, item, g_list, num)

                            else:
                                serverResponse1 = "Invalid subcommand!"

                        #send back client the response to the subrequest
                        print("echoTCPserver :: Sending edit mode response", serverResponse1)
                        clientConnection.send(serverResponse1.encode())

                else:
                    serverResponse = "Invalid command: \nValid commands are\n\tcatalog\n\tcreate\n\tedit\n\tdisplay\n\tdelete\n\texit\n"
                    print('echoTCPserver :: Sending server response ', serverResponse)
                    clientConnection.send(serverResponse.encode())

                # send back client the response tclientSocket.send(commandString.encode())
                #clientConnection.send(commandString.encode())	
                #print('echoTCPserver :: Sending server response ', serverResponse)
                #clientConnection.send(serverResponse.encode())

        clientConnection.close()

if __name__ == "__main__":
    sys.exit(main())
