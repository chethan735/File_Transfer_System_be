import socket
import threading
import hashlib
import random
import time

CHUNK_SIZE = 1024  # 1KB chunks
PORT = 5000
DROP_PROBABILITY = 0.1  # 10% packets will be dropped
CORRUPT_PROBABILITY = 0.05  # 5% packets will be corrupted

def calculate_checksum(data):
    """Calculate SHA256 checksum of given data"""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()

def handle_client(client_socket, client_address):
    try:
        print(f"[+] Connected: {client_address}")

        # Receive file name
        file_name = client_socket.recv(1024).decode()
        print(f"[*] Receiving file: {file_name} from {client_address}")

        # Receive file size
        file_size = int(client_socket.recv(1024).decode())
        received_data = bytearray()

        # Receive file chunks
        expected_seq = 0
        while len(received_data) < file_size:
            packet = client_socket.recv(CHUNK_SIZE + 8)  # 4 bytes for seq number, 4 for ID
            if not packet:
                break

            seq_num = int.from_bytes(packet[:4], 'big')
            client_id = int.from_bytes(packet[4:8], 'big')
            chunk_data = packet[8:]

            # Simulating packet loss
            if random.random() < DROP_PROBABILITY:
                print(f"[!] Dropping packet {seq_num} from {client_address}")
                continue

            # Simulating corruption
            if random.random() < CORRUPT_PROBABILITY:
                chunk_data = bytearray(chunk_data)
                chunk_data[0] = chunk_data[0] ^ 0xFF  # Flip bits to corrupt
                print(f"[!] Corrupting packet {seq_num} from {client_address}")

            # Send ACK
            client_socket.sendall(seq_num.to_bytes(4, 'big'))

            if seq_num == expected_seq:
                received_data.extend(chunk_data)
                expected_seq += 1

        # Compute checksum
        file_checksum = calculate_checksum(received_data)

        # Send checksum to client
        client_socket.sendall(file_checksum.encode())

        # Send back the file
        print(f"[*] Sending back file to {client_address}")
        expected_seq = 0
        for i in range(0, len(received_data), CHUNK_SIZE):
            chunk = received_data[i:i + CHUNK_SIZE]
            seq_num_bytes = expected_seq.to_bytes(4, 'big')
            client_id_bytes = (client_address[1] % 10000).to_bytes(4, 'big')

            # Simulate drop and corruption
            if random.random() < DROP_PROBABILITY:
                print(f"[!] Dropping packet {expected_seq} (resend later)")
                continue
            if random.random() < CORRUPT_PROBABILITY:
                chunk = bytearray(chunk)
                chunk[0] = chunk[0] ^ 0xFF
                print(f"[!] Corrupting packet {expected_seq}")

            client_socket.sendall(seq_num_bytes + client_id_bytes + chunk)
            expected_seq += 1

        print(f"[+] File transfer complete for {client_address}")

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(5)
    print(f"[*] Server listening on port {PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
