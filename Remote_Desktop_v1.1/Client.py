import socket
import cv2
import pickle
import struct
import ssl
import pyautogui

server_ip = "192.168.166.105"  # Change this to your server's IP

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

context = ssl.create_default_context()
context.load_verify_locations("server.crt")  # Trust the server certificate

conn = context.wrap_socket(client_socket, server_hostname=server_ip)
conn.connect((server_ip, 9999))
print("✅ Connected to server.")

try:
    while True:
        # Receive frame size
        data_size = struct.unpack("Q", conn.recv(8))[0]

        # Receive image data
        data = b""
        while len(data) < data_size:
            data += conn.recv(4096)

        # Decode and display frame
        frame = pickle.loads(data)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        cv2.imshow("Live Remote Desktop", frame)

        # Send mouse position
        x, y = pyautogui.position()
        conn.sendall(f"MOUSE_MOVE {x} {y}".encode())

        if cv2.waitKey(1) == ord("q"):  # Press 'q' to quit
            break

except Exception as e:
    print(f"❌ Error: {e}")

conn.close()
cv2.destroyAllWindows()
