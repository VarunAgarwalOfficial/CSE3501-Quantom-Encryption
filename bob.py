import socket
import random
import math

# Constants for encryption
PADDING_LITERAL = " "
KEY_BATCH_SIZE = 7
FIRST_KEY_LENGTH = 500

# Convert binary to decimal
def binary_to_decimal(binary):
    decimal, i = 0, 0
    while binary != 0:
        dec = binary % 10
        decimal += dec * pow(2, i)
        binary //= 10
        i += 1
    return decimal   

# Generate a list of decimal keys from a binary key
def generate_decimal_key(binary_key):
    decimal_key = [binary_to_decimal(int(binary_key[i : i + KEY_BATCH_SIZE])) for i in range(0, len(binary_key), KEY_BATCH_SIZE)]
    return decimal_key

# Encrypt a message using XOR with the final key
def xor_encrypt(message, final_key):
    encrypted_msg = ""
    for i in range(len(message)):
        encrypted_msg += chr(ord(message[i]) ^ final_key[i % len(final_key)])
    return encrypted_msg

# Server configuration
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
SERVER = "10.0.0.107"
ADDR = (SERVER, PORT)

# Client setup
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(ADDR)
accepted_filters = ["R", "D"]

# Send the message securely
def send_secure_message(unencrypted_msg):
    # Generate a random binary key and construct the message
    binary_key = []
    filters_used = []

    for _ in range(FIRST_KEY_LENGTH):
        bit = random.choice([0, 1])
        binary_key.append(bit)
        chosen_filter = random.choice(accepted_filters)
        filters_used.append(chosen_filter.lower() if bit == 0 else chosen_filter)
    
    message = "".join(filters_used).encode(FORMAT)
    client_socket.send(message)

    # Send the list of filters used
    client_socket.send("".join(filters_used).encode(FORMAT))

    # Receive accepted filters
    final_key = [binary_key[i] for i in range(FIRST_KEY_LENGTH) if client_socket.recv(1).decode(FORMAT) == "1"]
    print("Final Key:", "".join(map(str, final_key)))

    # Create the final key
    final_key = generate_decimal_key("".join(map(str, final_key)))
    print(f"Final key created using the binary key with key batch: {KEY_BATCH_SIZE} is: {final_key}")

    # Calculate required parameters for encryption
    key_length = len(final_key)
    batch_size = math.ceil(len(unencrypted_msg) / key_length)

    # Send batch size to the server
    client_socket.send(str(batch_size).encode(FORMAT))

    # Pad the message if needed
    unencrypted_msg = unencrypted_msg + PADDING_LITERAL * (batch_size * 500 - len(unencrypted_msg))

    # Display information
    print(f"Size of the message: {len(unencrypted_msg)}")
    print(f"Batch size: {batch_size}")
    print(f"Padding Literal: {PADDING_LITERAL}")

    # Encrypt and send the message
    encrypted_msg = xor_encrypt(unencrypted_msg, final_key)
    print(f"Encrypted message: {encrypted_msg.encode(FORMAT)}")
    client_socket.send(encrypted_msg.encode(FORMAT))

if __name__ == "__main__":
    unencrypted_msg = str(input("Enter message: "))
    send_secure_message(unencrypted_msg)
