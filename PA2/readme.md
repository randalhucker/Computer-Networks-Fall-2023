# README 

Group Members: Randy Hucker, Steven Habra, Sam Graler

This document contains important usability information for our submission of the following assignemnt:

CS4065 Computer Networks and Networked Computing
Project 2 - A Simple Bulletin Board Using Socket Programming
Instructor: Giovani Abuaitah

## Instructions for compilation

No additional libraries or packages are needed to run these programs.

In order to compile and run the client / server, one must simply run the `launch_client.py` and `launch_server.py` files respectively. If you are working out of a terminal, this is as simple as running the following commands (the terminal must be working out of the root project directory):
* Server: `python launch_server.py`
* Client: `python launch_client.py`

Both programs support command line options to specify the IP address and port to which the client must connect, which can be viewed by running the above command with the addition of a `-h` or `--help` flag. A summry will be provided below:
* Client Options:
    * -h, --help   show this help message and exit
    * --ip IP      Server IP address
    * --port PORT  Server port number
The address of the server and port are preset, but if they were to be changed, the client command line options could be used to connect to it. If the client is run without options, its default connection settings are the same as the server's

## Usabiliy Instructions

Once the client connects to the server, it will prompt the user to enter their name. Afte this occurs, the general 'Enter Message: ' prompt will be displayed. All input is entered to this prompt. 

Our program allows the user to send a message to their current group (begins as default) by simply typing what they wish to send.

Messages must be entered in the following format: 'subject' message
* subject is an optional field, if left empty the message will be sent without a subject

To use a command, the user must type a '!' character followed by a command from the list below. Each command is given with a description of the arguments they require and what it their function is.

Note: Pay attention to the description of each command as the naming convention of each function is different than what is outlined in the project description.

Commands:                           
* !get_groups                     
    * This command returns a list of the groups created
    * This command takes no arguments
* !join 'group_name'              
    * This command will allow the user to join a group that they specify 
    * If the group does not already exist, it will create it
    * The group name must be specified between single quotes as displayed above
* !send 'group_name' message      
    * This command allows a client to send a message to a group of their choice
    * Once again, The group name must be specified between single quotes as displayed above
    * The message must follow the format described earlier in this section
* !get_members 'group_name'       
    * This command returns a list of users that are in the specified group
    * The group name must be specified between single quotes as displayed above
* !leave 'group_name'             
    * This command will allow the client to leave the group specific
    * The group name must be specified between single quotes as displayed above
* !get_message 'id' 'group_name'  
    * This command will return the message from the given group with the given id 
    * The group name and id must be specified between single quotes as displayed above
* !switch 'group_name'            
    * This command will switch you "current" group
    * This means that when you send a message without using a command, it will be sent to the group you specify
    * Everyone's default current group is 'default'
* !disconnect                     
    * The command will disconnect you from the server
* !help                           
    * This command will output the help string to remind the user of available functionality

IMPORTANT: Group names may NOT contain single quotes!

## Major Challenges

The biggest challenge we encountered in this project was finding a way for a client to be able to receive and send messgaes at the same time. In order to solve this, we came up with the idea to use an additional thread on the client side as a daemon. This daemon thread sits and waits for incoming messages, and when it receives one, executes the steps necessary to display it, and then returns to waiting for more messages. The other client thread is the one that waits for user input and send messages to the server and other clients.

Apart from that, most of the difficulties we encountered were trivial, related to invalid JSON objects or deciding what to display on the client side.