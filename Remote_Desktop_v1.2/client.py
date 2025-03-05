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

PACKET_SIZE = 4096  # UDP packet size


def receive_data(sock, total_chunks):
    """Receive all chunks of data and reassemble."""
    data = b""
    for _ in range(total_chunks):
        chunk, _ = sock.recvfrom(PACKET_SIZE)
        data += chunk
    return data


try:
    while True:
        # Receive Total Chunk Count
        total_chunks_data, _ = client_socket.recvfrom(8)
        total_chunks = struct.unpack("Q", total_chunks_data)[0]

        # Receive Full Image Data in Chunks
        data = receive_data(client_socket, total_chunks)
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
