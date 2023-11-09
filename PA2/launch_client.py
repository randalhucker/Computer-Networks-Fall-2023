from client import *
import argparse

def main():
    parser = argparse.ArgumentParser(description="Client for connecting to a message board server")
    parser.add_argument("--ip", type=str, default="localhost", help="Server IP address")
    parser.add_argument("--port", type=int, default=8080, help="Server port number")
    args = parser.parse_args()

    client = Client(host=args.ip, port=args.port)
    client.start()

if __name__ == "__main__":
    main()
