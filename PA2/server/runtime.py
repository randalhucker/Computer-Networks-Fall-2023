import socket
import threading
import logging
import json
import re
from groups import Group
from typing import Dict, Tuple, List


class Server:
    """This class will handle the server side of the chat application. It will handle multiple clients and will send messages to all connected clients."""

    # Initialize the server class
    def __init__(self, host="localhost", port=8080):
        self.addr = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[
            socket.socket, Tuple[str, str]
        ] = {}  # Use a dictionary to store connected clients
        self._logger = logging.getLogger(__name__)
        self._format = "utf-8"
        self.lock = threading.Lock()  # Use an instance lock for thread safety
        self.groups: Dict[str, Group] = {
            "default": Group("default", "default"),
            "group_1": Group("group_1", "group 1"),
            "group_2": Group("group_2", "group 2"),
            "group_3": Group("group_3", "group 3"),
            "group_4": Group("group_4", "group 4"),
        }

    def new_group(self, group_name: str, original_name: str):
        """Adds a group to the server.

        Args:
            group_name (str): The name of the group.
            original_name (str): The original name of the group.
        """
        self.groups[group_name] = Group(group_name, original_name)

    def send_message(
        self,
        client: socket.socket,
        message: dict[str, str],
        group_name: str = "default",
        to_caller: bool = False,
    ):
        """Sends a message to all connected clients.

        Args:
            client (socket.socket): The client socket.
            message (str): The message to send.
            group_name (str): The name of the group to send the message to.
            to_caller (bool): Whether or not to send the message to the caller.
        """

        user_name = message["name"]  # Get the user's name
        user_message = message["message"]  # Get the user's message
        user_subject = ""  # Initialize the user's subject
        try:
            user_subject = message["subject"].replace(
                "\n", ""
            )  # Get the user's subject
        except KeyError:
            pass

        if not user_message:
            return  # Skip sending empty messages

        json_data = {
            "name": user_name,
            "message": user_message,
            "subject": user_subject,
            "group": group_name,
        }

        try:
            if message["id"]:
                json_data["id"] = message["id"]
            if message["date"]:
                json_data["date"] = message["date"]
            if message["subject"]:
                json_data["subject"] = message["subject"]
        except KeyError:
            pass

        if not to_caller:
            with self.lock:
                self.groups[group_name].new_message(
                    message
                )  # Add the message to the log
                json_data["id"] = message["id"]  # Add the message id to the JSON data
                json_data["date"] = message[
                    "date"
                ]  # Add the message date to the JSON data
                json_data["subject"] = message[
                    "subject"
                ]  # Add the message subject to the JSON data

        json_string = json.dumps(json_data)  # Convert the dictionary to a JSON string

        if not to_caller:
            users = self.groups[group_name].get_all_users().values()
            for c in users:
                if c[0] != client:
                    self._send_message(
                        c[0], json_string
                    )  # Send the JSON string to other clients
        else:
            # TODO error here
            self._send_message(
                client, json_string
            )  # Send the JSON string to the current client

    def _send_message(self, client: socket.socket, dump: str):
        """Sends a message to a client.

        (Args):
            client (socket.socket): The client socket.
            dump (str): The message to send.
        """
        client.sendall(dump.encode(encoding=self._format))

    def send_last_two_messages(self, client: socket.socket, group_name: str):
        """Sends the last two messages in the group to the client.

        Args:
            client (socket.socket): The client socket.
        """
        with self.lock:
            last_messages = self.groups[group_name].get_last_two_messages()
            for message in last_messages:
                self.send_message(client, message, group_name, to_caller=True)

    def join_group(self, client: socket.socket, group_name: str, user_name: str):
        """Adds a client to a group. Creates a new group if the group does not exist.

        Args:
            client (socket.socket): The client socket.
            group_name (str): The name of the group.
            user_name (str): The name of the user.
        """
        _, address = self.clients[client]
        with self.lock:
            self.groups[group_name].join(user_name, (client, address))
        user_message = {
            "name": "Server",
            "message": "Members: "
            + str([str(key) for key in self.groups[group_name].get_all_users().keys()]),
        }
        self.send_message(client, user_message, to_caller=True)
        self.send_last_two_messages(client, group_name)

    def get_all_groups(self) -> List[str]:
        """Returns a list of all groups.

        Returns:
            List[str]: A list of all groups.
        """
        return [group.get_original_name() for group in self.groups.values()]

    def disconnect(
        self, client: socket.socket, name: str
    ) -> dict[str, str]:
        """Disconnects a client from the server.

        Args:
            client (socket.socket): The client socket.
            address (str): The address of the client.
            name (str): The name of the client.
        """
        self.clients.pop(client)
        user_message = {
            "name": "CLIENT DISCONNECTED",
            "message": name + " disconnected.",
        }
        for group in self.groups.values():
            if group.is_user_in_group(name):  # If the user is in the group,
                group.leave(name)  # Remove the user from the group
        return user_message

    def get_message_by_id(self, id: int, group_name: str) -> dict[str, str]:
        """Returns a message by its id.

        Args:
            id (int): The id of the message.
            group_name (str): The name of the group.

        Returns:
            dict[str, str]: The message.
        """
        with self.lock:
            return self.groups[group_name].get_message_by_id(id)

    def handle_client(self, client: socket.socket, address):
        """Will handle a client connection. This function will run in a separate thread.

        Args:
            client (socket.socket): The client socket.
            address (str): The address of the client.
        """
        self._logger.info(
            f"[NEW CONNECTION] {address} connected."
        )  # Log the connection
        # Send an initial message to the client
        initial_msg = {
            "name": "Server",
            "message": "Successfully connected to the server. Type !help for a list of commands.",
            "subject": "",
        }
        initial_msg_string = json.dumps(
            initial_msg
        )  # Convert the dictionary to a JSON string
        client.send(
            initial_msg_string.encode(encoding=self._format)
        )  # Send the JSON string

        # Send the last 2 messages in the group to the client
        self.send_last_two_messages(client, "default")

        connected = True
        msg = client.recv(1024).decode(self._format)  # Receive 1024 bytes of data
        received_json = json.loads(msg)  # Convert the JSON string to a dictionary
        user_name = received_json["name"]
        with self.lock:
            self.groups["default"].join(user_name, (client, address))
            self.clients.update({client: [user_name, address]})
        join_msg = {"name": "Server", "message": user_name + " has joined the chat."}
        self.send_message(client, join_msg)  # Send the message to all connected clients
        current_group = "default"
        while connected:
            try:
                user_message_string = client.recv(1024).decode(
                    self._format
                )  # Receive 1024 bytes of data

                messages = self.parse_json_string(
                    user_message_string
                )  # Parse the JSON string

                for user_message in messages:
                    if not user_message["message"]:  # If the message is empty,
                        continue  # Skip the rest of the loop

                    command = user_message["message"].split(" ")[0].lower()

                    if command == "!disconnect":  # If the user wants to disconnect,
                        with self.lock:
                            connected = False
                            user_message = self.disconnect(
                                client, user_message["name"]
                            )

                    if command == "!join":
                        string = user_message.get("message", "")
                        match = re.search(r"'([^']+?)'", string)

                        if match:
                            group_name = (
                                match.group(1).replace(" ", "_").replace("'", "")
                            )
                            if group_name not in self.get_all_groups():
                                self.new_group(group_name, match.group(1))
                            self.join_group(client, group_name, user_message["name"])
                        continue

                    if command == "!get_message":
                        string = user_message.get("message", "")
                        matches: List[str] = re.findall(r"'([^']+?)'", string)
                        if matches:
                            message_id = int(matches[0])
                            group_name = matches[1].replace(" ", "_")
                            user_message = self.get_message_by_id(
                                message_id, group_name
                            )
                            self.send_message(
                                client, user_message, group_name, to_caller=True
                            )
                        continue

                    if command == "!get_groups":
                        user_message = {
                            "name": "Server",
                            "message": "Groups: " + str(self.get_all_groups()),
                        }
                        self.send_message(client, user_message, to_caller=True)
                        continue

                    if command == "!get_members":
                        string = user_message.get("message", "")
                        match = re.search(r"'([^']+?)'", string)
                        if match:
                            group_name = match.group(1).replace(" ", "_")
                            user_message = {
                                "name": "Server",
                                "message": "Members: "
                                + str([member for member in self.groups[group_name].get_all_users().keys()]),
                            }
                            self.send_message(client, user_message, to_caller=True)
                        continue

                    if command == "!send":
                        string = user_message.get("message", "")
                        matches = re.findall(r"'([^']+?)'", string)
                        if matches:
                            group_length = len(matches[0]) + 2
                            group_name = matches[0].replace(" ", "_").replace("'", "")
                            command_length = len(command) + group_length + 2

                            subject = user_message["subject"]
                            subject_length = len(subject)
                            if len(matches) > 1:
                                subject_length = len(matches[1]) + 3
                                subject = matches[1]

                            message = user_message["message"][
                                command_length + subject_length :
                            ]

                            user_message = {
                                "name": user_message["name"],
                                "message": message,
                                "subject": subject,
                            }

                            self.send_message(
                                client,
                                user_message,
                                group_name,
                            )
                            continue

                    if command == "!switch":
                        string = user_message.get("message", "")
                        match = re.search(r"'([^']+?)'", string)
                        if match:
                            group_name = match.group(1).replace(" ", "_")
                            users = self.groups[group_name].get_all_users().keys()
                            if (group_name in self.get_all_groups()) and (
                                user_message["name"] in users
                            ):
                                current_group = group_name
                            # add a message indicating user doesn't belong to group or the group doesn't exist
                        continue

                    if command == "!leave":
                        string = user_message.get("message", "")
                        match = re.search(r"'([^']+?)'", string)
                        if match:
                            group_name = match.group(1).replace(" ", "_")
                            if group_name in self.get_all_groups():
                                self.groups[group_name].leave(user_message["name"])
                        continue

                    if command == "!help":
                        help_message = """

Messages must be entered in the following format:
    'subject' message               (subject is an optional field)

Group names may not contain special characters: 
                                    (use underscores instead) 

Commands:                           
    !get_groups                     (get a list of the groups created)
    !join 'group_name'              (join a group)
    !send 'group_name' message      (send a message to a group)
    !get_members 'group_name'       (return the members of a group)
    !leave 'group_name'             (leave group)
    !get_message 'id' 'group_name'  (get message with id from a group)
    !switch 'group_name'            (switch current message context to a different group)
    !disconnect                     (disconnect from the server)
    !help                           (display this help message)
"""

                        user_message = {
                            "name": "Server",
                            "message": help_message,
                            "subject": "",
                        }
                        self.send_message(client, user_message, to_caller=True)
                        continue

                    self.send_message(
                        client, user_message, current_group
                    )  # Send the message to all connected clients
            except Exception as e:
                self._logger.error(f"Error handling client: {e}")
        self._logger.info(f"[DISCONNECTION] {address} disconnected.")
        self._logger.info(f"[ACTIVE CONNECTIONS] {len(self.clients)}")
        client.close()

    def parse_json_string(self, json_string: str) -> List[Dict[str, str]]:
        # Initialize an empty list to store dictionaries
        parsed_list = []

        # Split the input string into individual JSON objects
        json_objects = json_string.split("}{")

        # Handle cases where there are missing curly braces at the beginning or end
        if len(json_objects) > 1:
            json_objects[0] = json_objects[0] + "}"
            json_objects[-1] = "{" + json_objects[-1]

        # Iterate through the JSON objects and parse them
        for obj in json_objects:
            try:
                # Load each JSON object into a dictionary
                parsed_dict = json.loads(obj)
                parsed_list.append(parsed_dict)
            except json.JSONDecodeError:
                # Handle any JSON decoding errors (invalid JSON)
                self._logger.info(f"Skipping invalid JSON object: {obj}")

        return parsed_list

    def start(self):
        try:
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
            )  # Allow the socket to be reused
            self.socket.bind(self.addr)
            self.socket.listen()

            print(f"[LISTENING] Server is listening on {self.addr[0]}:{self.addr[1]}")
            while True:
                client, address = self.socket.accept()
                with self.lock:
                    self.clients[client] = ["", address]
                    thread = threading.Thread(
                        target=self.handle_client, args=(client, address)
                    )
                    thread.start()
                    self._logger.info(f"[ACTIVE CONNECTIONS] {len(self.clients)}")
        except KeyboardInterrupt:
            self._logger.info("[SERVER STOPPED] Server stopped by user.")
        except Exception as e:
            self._logger.error(f"Error: {e}")
        finally:
            self.socket.close()
