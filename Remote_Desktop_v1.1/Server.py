import socket
import cv2
import pickle
import struct
import pyautogui
import numpy as np
import threading
import ssl
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key

# Setup Mouse and Keyboard Controllers
mouse = MouseController()
keyboard = KeyboardController()

# Create and Secure Server Socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 9999))  # Listen on all interfaces
server_socket.listen(5)  # Allow multiple clients

# SSL Context Setup
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

print("✅ Server is running... Waiting for connections.")

def handle_client(conn):
    """Handle individual client connections securely."""
    conn = context.wrap_socket(conn, server_side=True)  # Secure connection
    print(f"🔗 Client connected: {conn.getpeername()}")

    try:
        while True:
            # Capture Screen
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Encode Frame
            _, encoded_frame = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            data = pickle.dumps(encoded_frame)

            # Send Frame Size and Data
            conn.sendall(struct.pack("Q", len(data)) + data)

            # Receive Remote Control Commands
            command = conn.recv(1024).decode()
            if command:
                process_command(command)

    except Exception as e:
        print(f"❌ Error: {e}")

    conn.close()

def process_command(command):
    """Process received mouse and keyboard commands."""
    try:
        parts = command.split()
        action = parts[0]

        if action == "MOUSE_MOVE":
            x, y = int(parts[1]), int(parts[2])
            mouse.position = (x, y)

        elif action == "MOUSE_CLICK":
            mouse.click(Button.left)

        elif action == "KEY_PRESS":
            key = parts[1]
            if hasattr(Key, key):
                keyboard.press(getattr(Key, key))
                keyboard.release(getattr(Key, key))
            else:
                keyboard.press(key)
                keyboard.release(key)

    except Exception as e:
        print(f"❌ Command Error: {e}")

# Accept multiple clients
while True:
    client_conn, _ = server_socket.accept()
    threading.Thread(target=handle_client, args=(client_conn,), daemon=True).start()
