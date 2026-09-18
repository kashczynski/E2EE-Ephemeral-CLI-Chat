import sys
import server
import client

def main():
    if len(sys.argv)<2:
        print("USage")
        print(" python cli.py  start")
        print("  python cli.py connect")
        sys.exit(1)
    command=sys.argv[1].lower()

    if command=="start":
        print("[CLI] Launching Broadcast Server...")
        server.start_server()
    elif command=="connect":
        print("[CLI] Connecting to Broadcast Server...")
        client.start_client()
    else:
        print(f"Unknown command: '{command}'")
        print("Available commands: 'start', 'connect'")

if __name__ == "__main__":
    main()