import socket
import threading
import logging
import json
import re
from typing import List, Dict, Tuple

logging.basicConfig(level=logging.INFO)


class Client:
    def __init__(self, host, port):
        self.addr = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._logger = logging.getLogger(__name__)
        self._format = "utf-8"
        self.lock = threading.Lock()
        self.connected = False
        self.name = input("Enter name: ")

    def send(self, msg: str) -> bool:
        """This method sends a message to the server.

        Args:
            msg (str): The message to send to the server.

        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        try:
            subject = ""
            message = msg.strip()

            match = re.match(r"'(.*?)'(.*)", msg)

            if match:
                subject = match.group(1).strip()
                message = match.group(2).strip()

            response_data = {"name": self.name, "message": message, "subject": subject}
            response_string = json.dumps(response_data)
            with self.lock:
                self.socket.sendall(response_string.encode(encoding=self._format))
            return True
        except Exception as e:
            self._logger.error(f"Error sending message: {e}")
            return False

    def recv(self) -> List[Dict[str, str]]:
        """This method receives a message from the server. It will return a list of dictionaries containing the parsed JSON objects.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the parsed JSON objects. Name and message are the keys.
        """
        try:
            json_message_string = self.socket.recv(1024).decode(self._format)
            messages = self.parse_json_string(json_message_string)
            return messages
        except Exception as e:
            self._logger.error(f"Error receiving message: {e}")
            return []

    def receive_messages(self) -> None:
        """Daemon thread that receives messages from the server and prints them to the console. This thread will run until the client disconnects from the server."""
        while True:
            try:
                received_msgs = self.recv()
                if not self.connected:
                    break

                with self.lock:
                    for message in received_msgs:
                        if message["message"]:
                            print("\r                            ", end="")
                            if "group" in message:
                                group_str = f"[{message['group']}]"
                            else:
                                group_str = ""

                            if "id" in message:
                                id_str = f"[{message['id']}]"
                            else:
                                id_str = ""

                            if "name" in message:
                                name_str = f"[{message['name']}]"
                            else:
                                name_str = ""

                            if "date" in message:
                                date_str = f"[{message['date']}]"
                            else:
                                date_str = ""

                            subject_str = message.get("subject", "N/A")
                            if subject_str != "":
                                subject_str = " *" + subject_str + "*"
                            message_str = message.get("message", "N/A")

                            print(
                                f"\r{group_str}{id_str}{name_str}{date_str}{subject_str}: {message_str}"
                            )
                    if not self.name:
                        print("\rEnter name: ", end="")
                    else:
                        print("\rEnter message: ", end="")
            except Exception as e:
                if self.connected:
                    self._logger.error(f"Error receiving message: {e}")

    def parse_json_string(self, json_string: str) -> List[Dict[str, str]]:
        """This method parses a JSON string into a list of dictionaries.

        Args:
            json_string (str): The JSON string to parse.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the parsed JSON objects. Name and message are the keys.
        """
        parsed_list = []

        if not json_string:
            return parsed_list

        json_objects = json_string.split("}{")

        if len(json_objects) > 1:
            json_objects[0] = json_objects[0] + "}"
            json_objects[-1] = "{" + json_objects[-1]

        for obj in json_objects:
            try:
                parsed_dict = json.loads(obj)
                parsed_list.append(parsed_dict)
            except json.JSONDecodeError:
                self._logger.error(f"Skipping invalid JSON object: {obj}")

        return parsed_list

    def start(self):
        """
        This function starts the client. It will connect to the server and start a
        daemon thread to receive messages from the server. It will then prompt the user
        for a name and send messages to the server until the user enters "!disconnect".
        """
        try:
            while True:
                try:
                    self.socket.connect(self.addr)
                    break  # Break out of the loop if connection is successful
                except ConnectionRefusedError:
                    print("[ERROR] Connection refused.")
                    try:
                        host = input("Enter new host: ")
                        port = input("Enter new port: ")

                        # Validate host and port
                        if not host or not port.isdigit():
                            print(
                                "[ERROR] Invalid input. Please provide a valid host and port."
                            )
                            continue  # Restart the loop for new input

                        self.addr = (host.strip(), int(port))

                        # Close the existing socket before reconnecting
                        self.socket.close()
                        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    except ValueError:
                        print(
                            "[ERROR] Invalid port. Please enter a valid integer port."
                        )
                        continue  # Restart the loop for new input

            if self.name:
                msg = "has connected."
                self.send(msg)

            print(f"[CONNECTED] Connected to server on {self.addr[0]}:{self.addr[1]}")

            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()

            self.connected = True
            while self.connected:
                if not self.name:
                    msg = input("\rEnter name: ")
                    with self.lock:
                        self.name = msg
                        msg = "has connected."
                else:
                    msg = input("\rEnter message: ")
                    if not msg:
                        continue
                if msg.lower() == "!disconnect":
                    with self.lock:
                        self.connected = False
                self.send(msg)

        except Exception as e:
            self._logger.error(f"Error: {e}")

        finally:
            print("[DISCONNECTED] Disconnected from server.")
            self.recv()
            self.socket.close()
