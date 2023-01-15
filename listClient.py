#!/usr/bin/python3
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OSU ID: <zhang.11041>
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# listclient -- using TCP/IP to manage the list on the server
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
processingUserInput=True                   # Flag for processing
falseCommand = True
falseSubCommand = True
g_file = 'groceries.json'                  # the groceires json.file as the database of shopping lists

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def convert():
    with open(g_file) as json_file:

        data = json.load(json_file)
    return data

def listLength(index, g_list):
    d = g_list[index]
    key = list(d.keys())[0]
    return len(d.get(key))


def wait_response(clientSocket):
    serverResponse=clientSocket.recv(2048)
    serverResponse=serverResponse.decode()
    print('echoTCPclient :: Server response received ',serverResponse)

def send_subrequest(clientSocket, subCommandStr):
    clientSocket.send(subCommandStr.encode())
    # Wait for server response to subcommand
    serverResponse1 = clientSocket.recv(2048).decode()

#···············································································
# Application Main

#
def main():
	# get the IP and port from the configuration file
	config = ConfigParser()
	config.read('config.ini')
	serverIP = config['default']['host']
	serverPort = int(config['default']['port'])
	serverAddress=(serverIP,serverPort)
	logging.basicConfig(filename = 'list.log', format='%(asctime)s %(message)s', datefmt = '%a %b %d %l: %M:%S %Y', level = logging.INFO)

	#serverIP = getIP()
	#serverPort = getPort()
	#serverAddress=(serverIP,serverPort)
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Creates a TCP socket object using IPv4 as underlying network
	# 
	try:
		clientSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print('TCPclient :: Client socket object created')
		processingUserInput=True

		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		# Client connects to the server, three-way handshake performed
		#
		try:
			clientSocket.connect(serverAddress)
			print('TCPclient :: Connected to SIMPServer ',serverAddress)
			processingUserInput=True
		except:
			print('TCPclient :: Unable to connect to server ',serverAddress)
			processingUserInput=False

	except:
		print('TCPclient :: Unable to create client socket')
		processingUserInput=False

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# prompt for and receive command strings until close
	#
	while processingUserInput:
            print("\nenter again!!")
            processingEdit = True
            g_list = convert()
            length = len(g_list)
            commandString=input('TCPclient► ')
            print('echoTCPclient :: String received ',commandString)
	    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
            # serverResponse default to invalid for commandStrings other than the following cases
            #serverResponse = "Invalid!"
	    # prepare to stop if close
            num = 10000
            if (commandString[-1:]).isdigit():
                num = int(commandString[-1:])
            
            if commandString == 'exit':
                processingUserInput=False
                logging.info('REQUEST INFO %s the list sent', 'exit')
                # only send the valid request to the server
                print('echoTCPclient :: Sending client request ',commandString)
                clientSocket.send(commandString.encode())

            else:
                if commandString == 'catalog':
                    logging.info('REQUEST INFO %s the list received', 'catalog')
                    print('echoTCPclient :: Sending client request ',commandString)
                    clientSocket.send(commandString.encode())

                elif commandString.startswith('create'):
                    while len(commandString) < 8:
                        logging.info('ERROR INFO invalid %s command', 'create')
                        print("You must enter a title of the new list create follwed by a space after create\n")
                        commandString=input('TCPclient► ')
                    logging.info('REQUEST INFO %s the list received', 'create')
                    # only send the valid request to the server
                    print('echoTCPclient :: Sending client request ',commandString)
                    clientSocket.send(commandString.encode())

                elif commandString.startswith('delete'):
                    while not (len(commandString) == 8 and 0 <= num < length):
                        logging.info('ERROR INFO invalid %s command', 'delete')
                        print("You must enter a title in the range of the new list you want to create follwed by a space after delete\n")
                        commandString=input('TCPclient► ')
                        if (commandString[-1:]).isdigit():
                            num = int(commandString[-1:]) 

                    logging.info('REQUEST INFO %s the list received', 'delete')
                    # only send the valid request to the server
                    print('echoTCPclient :: Sending client request ',commandString)
                    clientSocket.send(commandString.encode())

                elif commandString.startswith('display'):
                    while not (len(commandString) == 9 and 0 <= num < length):
                        logging.info('ERROR INFO invalid %s command', 'display')
                        print("You must enter a title in the range of the new list you want to create follwed by a space after display\n")
                        commandString=input('TCPclient► ')
                        if (commandString[-1:]).isdigit():
                            num = int(commandString[-1:]) 

                    logging.info('REQUEST INFO %s the list received', 'display')
                    # only send the valid request to the server
                    print('echoTCPclient :: Sending client request ',commandString)
                    clientSocket.send(commandString.encode())

                elif commandString.startswith('edit'):
                    while not (len(commandString) == 6 and 0 <= num < length):
                        logging.info('ERROR INFO invalid %s command', 'edit')
                        print("You must enter a list number in the range of the list indexes follwed by a space after edit\n")
                        commandString = input('echoTCPclient► ')              
                        if (commandString[-1:]).isdigit():
                            num = int(commandString[-1:])

                    #only send the final valid edit request to the server
                    print('echoTCPclient :: Sending client request ',commandString)	
                    logging.info('REQUEST INFO enter %s mode received', 'edit')
                    clientSocket.send(commandString.encode())

                    list_length = listLength(num, g_list)

                    while processingEdit:
		                # deal with the sub commands
                        subCommandStr = input('TCPclient edit mode subcommand► ')
                        index = subCommandStr[-1]
                        if subCommandStr == 'quit':
                            processingEdit = False
                            logging.info('REQUEST INFO %s the edit mode received', 'quit')
                            
                            clientSocket.send("restart".encode())

                        else:
                            if subCommandStr == 'show':
                                logging.info('ERROR INFO invalid %s command', 'show')

                            elif subCommandStr.startswith('add'):
                                while not (len(subCommandStr) > 4):
                                    print("You must enter a nonempty string follwed by a space after add\n")
                                    subCommandStr = input('TCPclient edit mode subcommand► ')
                                    logging.info('ERROR INFO invalid %s command', 'add')

                            elif subCommandStr.startswith('remove'):
                                item = subCommandStr[7:len(subCommandStr)]
                                d = g_list[num]
                                list_value = d.get(list(d.keys())[0])
                                while (item not in list_value):
                                    print("You must enter a string in the list by a space after remove\n")
                                    subCommandStr = input('TCPclient edit mode subcommand► ')
                                    logging.info('ERROR INFO invalid %s command', 'remove')

                            else:
                                subCommandStr = input("Invalid command: \nValid commands are\n\tshow\n\tadd\n\tremove\n\tquit\n► ")

                        # Send the valid subcommand as the subrequest
                        clientSocket.send(subCommandStr.encode())
                        # Wait for server response to subcommand
                        serverResponse1 = clientSocket.recv(2048).decode()
                        print('TCPclient :: Server response received', serverResponse1)
                        
                else:
                    clientSocket.send(commandString.encode())

	    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
         
	        # Wait for server response
            serverResponse=clientSocket.recv(2048)
            serverResponse=serverResponse.decode()
            print('echoTCPclient :: Server response received ',serverResponse)

	clientSocket.close()

if __name__ == "__main__":
	sys.exit(main())
