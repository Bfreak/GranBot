import PicoRobotics
import utime
import network
import socket
import time
import sys

board = PicoRobotics.KitronikPicoRobotics()

# Wi-Fi Credentials
SSID = "WestburyWifiHorse"
PASSWORD = "TessJames1"

# Commands for robot control
def move_forwards():
    board.bothStep("f/r", 100, 3000)
    
def move_backwards():    
    board.bothStep("r/f", 100, 3000)
    
def turn_left():
    board.bothStep("f", 5, 5000)
    
def turn_right():
    board.bothStep("r", 5, 5000)


COMMANDS = {
    "up": move_forwards,
    "down": move_backwards,
    "left": turn_left,
    "right": turn_right,
}


# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Connecting to Wi-Fi...", end="")
    for _ in range(20):  # Wait up to 10 seconds
        if wlan.isconnected():
            print("\nConnected!")
            print("IP Address:", wlan.ifconfig()[0])
            return wlan.ifconfig()[0]
        print(".", end="")
        time.sleep(0.5)

    print("\nFailed to connect to Wi-Fi")
    sys.exit()

# HTML page with D-pad controls
HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Robot Controller</title>
    <style>
        body { text-align: center; font-family: Arial, sans-serif; }
        .button { width: 80px; height: 80px; font-size: 20px; margin: 5px; }
        .grid { display: grid; grid-template-columns: 100px 100px 100px; justify-content: center; }
    </style>
    <script>
        function sendCommand(command) {
            fetch('/' + command)
                .then(response => console.log(command + " sent"))
                .catch(error => console.error("Error:", error));
        }
    </script>
</head>
<body>
    <h2>Robot Controller</h2>
    <div class="grid">
        <div></div> <button class="button" onclick="sendCommand('up')">^</button> <div></div>
        <button class="button" onclick="sendCommand('left')"><</button>
        <button class="button" onclick="sendCommand('right')">></button>
        <div></div> <button class="button" onclick="sendCommand('down')">v</button> <div></div>
    </div>
</body>
</html>
"""

def start_server():
    addr = connect_wifi()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((addr, 80))
    s.listen(5)

    print("Web server running at http://" + addr)

    while True:
        conn, addr = s.accept()
        request = conn.recv(1024).decode()
        print("Request from:", addr)
        print(request)

        # Extract command from the request
        for command in COMMANDS:
            if f"GET /{command} " in request:
                print("Command received:", command)
                COMMANDS[command]()  # Call the corresponding function
                break

        # Send HTML response
        conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
        conn.sendall(HTML)
        conn.close()

# Run the server
start_server()