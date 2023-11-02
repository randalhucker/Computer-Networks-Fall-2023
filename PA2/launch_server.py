from server import *
import argparse

def main():
    parser = argparse.ArgumentParser(description="Server for hosting a message board")
    parser.parse_args()

    server = Server()
    server.start()

if __name__ == '__main__':
    main()