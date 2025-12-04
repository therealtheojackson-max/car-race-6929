#!/usr/bin/env python3
"""Test account registration and login"""
import socket
import json
import time

HOST = 'localhost'
PORT = 50007

def send_msg(sock, msg_dict):
    """Send a message and receive response"""
    sock.sendall((json.dumps(msg_dict) + '\n').encode('utf-8'))
    time.sleep(0.1)
    response = b''
    sock.settimeout(1)
    try:
        response = sock.recv(4096)
    except socket.timeout:
        pass
    return response.decode('utf-8', errors='ignore')

def test_register():
    """Test account registration"""
    print("\n=== Testing Registration ===")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    
    # Receive auth_required
    auth_msg = sock.recv(1024).decode('utf-8')
    print(f"Auth msg: {auth_msg}")
    
    # Register new account
    print("\nRegistering 'testuser' with password 'pass1234'...")
    response = send_msg(sock, {'type': 'register', 'username': 'testuser', 'password': 'pass1234'})
    print(f"Response: {response}")
    
    sock.close()

def test_login():
    """Test account login"""
    print("\n=== Testing Login ===")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    
    # Receive auth_required
    auth_msg = sock.recv(1024).decode('utf-8')
    print(f"Auth msg: {auth_msg}")
    
    # Login
    print("\nLogging in with 'testuser' and 'pass1234'...")
    response = send_msg(sock, {'type': 'login', 'username': 'testuser', 'password': 'pass1234'})
    print(f"Response: {response}")
    
    sock.close()

def test_wrong_password():
    """Test login with wrong password"""
    print("\n=== Testing Login with Wrong Password ===")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    
    # Receive auth_required
    auth_msg = sock.recv(1024).decode('utf-8')
    print(f"Auth msg: {auth_msg}")
    
    # Try wrong password
    print("\nLogging in with 'testuser' and wrong password 'wrongpass'...")
    response = send_msg(sock, {'type': 'login', 'username': 'testuser', 'password': 'wrongpass'})
    print(f"Response: {response}")
    
    sock.close()

def test_duplicate_register():
    """Test registering duplicate account"""
    print("\n=== Testing Duplicate Registration ===")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    
    # Receive auth_required
    auth_msg = sock.recv(1024).decode('utf-8')
    print(f"Auth msg: {auth_msg}")
    
    # Try to register again
    print("\nAttempting to register 'testuser' again...")
    response = send_msg(sock, {'type': 'register', 'username': 'testuser', 'password': 'pass1234'})
    print(f"Response: {response}")
    
    sock.close()

def check_accounts_file():
    """Check what's in accounts.json"""
    print("\n=== Checking accounts.json ===")
    import os
    if os.path.exists('accounts.json'):
        with open('accounts.json', 'r') as f:
            data = json.load(f)
            print(json.dumps(data, indent=2))
    else:
        print("accounts.json does not exist yet")

if __name__ == '__main__':
    try:
        test_register()
        time.sleep(0.5)
        test_login()
        time.sleep(0.5)
        test_wrong_password()
        time.sleep(0.5)
        test_duplicate_register()
        time.sleep(0.5)
        check_accounts_file()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
