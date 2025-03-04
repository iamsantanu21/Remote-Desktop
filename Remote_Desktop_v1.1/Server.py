import socket
import cv2
import pickle
import struct
import pyautogui
import numpy as np
import threading
import ssl
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key

# Setup mouse and keyboard controllers
mouse = MouseController()
keyboard = KeyboardController()

# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 9999))
server_socket.listen(5)  # Allow multiple clients

# Secure with SSL
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

print("Waiting for connections...")

def handle_client(conn):
    conn = context.wrap_socket(conn, server_side=True)  # Secure the connection
    print(f"Client connected: {conn.getpeername()}")

    try:
        while True:
            # Capture screen
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Encode frame
            _, encoded_frame = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            data = pickle.dumps(encoded_frame)

            # Send frame size and data
            conn.sendall(struct.pack("Q", len(data)) + data)

            # Receive remote control commands
            command = conn.recv(1024).decode()
            if command:
                process_command(command)

    except Exception as e:
        print(f"Error: {e}")
    
    conn.close()

def process_command(command):
    """ Process received mouse and keyboard commands. """
    parts = command.split()
    if parts[0] == "MOUSE_MOVE":
        x, y = int(parts[1]), int(parts[2])
        mouse.position = (x, y)
    elif parts[0] == "MOUSE_CLICK":
        mouse.click(MouseController().Button.left)
    elif parts[0] == "KEY_PRESS":
        key = parts[1]
        keyboard.press(Key[key] if key in Key.__dict__ else key)
        keyboard.release(Key[key] if key in Key.__dict__ else key)

# Accept multiple clients
while True:
    client_conn, _ = server_socket.accept()
    threading.Thread(target=handle_client, args=(client_conn,)).start()
