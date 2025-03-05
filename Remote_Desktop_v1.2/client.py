import socket
import cv2
import pickle
import struct
import pyautogui

server_ip = "192.168.166.105"  # Replace with actual server IP

# Create UDP Client Socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send Initial Connection Packet
client_socket.sendto("CONNECT".encode(), (server_ip, 9999))
print("✅ Connected to server.")


def receive_data(sock, size):
    """Helper function to receive exact bytes"""
    data, _ = sock.recvfrom(size)
    return data


try:
    while True:
        # Receive Frame Size
        data_size_bytes = receive_data(client_socket, 8)
        data_size = struct.unpack("Q", data_size_bytes)[0]

        # Receive Full Image Data
        data, _ = client_socket.recvfrom(data_size)
        frame = pickle.loads(data)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        # Show Frame
        cv2.imshow("Live Remote Desktop", frame)

        # Send Mouse Position
        x, y = pyautogui.position()
        client_socket.sendto(f"MOUSE_MOVE {x} {y}".encode(), (server_ip, 9999))

        # Quit on 'q' Press
        if cv2.waitKey(1) == ord("q"):
            break
except Exception as e:
    print(f"❌ Error: {e}")

client_socket.close()
cv2.destroyAllWindows()
