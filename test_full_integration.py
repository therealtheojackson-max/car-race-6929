#!/usr/bin/env python3
"""Comprehensive integration test for account system and chat"""
import socket
import json
import time
import subprocess
import os
import signal

def test_account_flow():
    """Test the complete account flow: register, login, chat, logout, re-login"""
    print("\n" + "="*60)
    print("ACCOUNT SYSTEM INTEGRATION TEST")
    print("="*60)
    
    test_username = f"testplayer_{int(time.time())}"
    test_password = "secure_pass_123"
    
    # Test 1: Register new account
    print(f"\n[TEST 1] Registering new account: {test_username}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('localhost', 50007))
        auth_msg = sock.recv(1024).decode('utf-8')
        print(f"  ✓ Connected, received: {json.loads(auth_msg).get('type')}")
        
        reg_msg = {'type': 'register', 'username': test_username, 'password': test_password}
        sock.sendall((json.dumps(reg_msg) + '\n').encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        result = json.loads(response)
        
        if result.get('success'):
            print(f"  ✓ Registration successful: {result.get('message')}")
        else:
            print(f"  ✗ Registration failed: {result.get('message')}")
            return False
    finally:
        sock.close()
    
    time.sleep(0.2)
    
    # Test 2: Login with correct password
    print(f"\n[TEST 2] Login with correct password")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('localhost', 50007))
        auth_msg = sock.recv(1024).decode('utf-8')
        
        login_msg = {'type': 'login', 'username': test_username, 'password': test_password}
        sock.sendall((json.dumps(login_msg) + '\n').encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        result = json.loads(response)
        
        if result.get('success'):
            print(f"  ✓ Login successful: {result.get('message')}")
        else:
            print(f"  ✗ Login failed: {result.get('message')}")
            return False
        
        # Test 3: Send message after login
        print(f"\n[TEST 3] Send chat message after authentication")
        join_msg = {'type': 'join', 'username': test_username}
        sock.sendall((json.dumps(join_msg) + '\n').encode('utf-8'))
        time.sleep(0.2)
        
        chat_msg = {'type': 'msg', 'username': test_username, 'text': 'Hello from test!'}
        sock.sendall((json.dumps(chat_msg) + '\n').encode('utf-8'))
        print(f"  ✓ Chat message sent successfully")
        
    finally:
        sock.close()
    
    time.sleep(0.2)
    
    # Test 4: Login with wrong password
    print(f"\n[TEST 4] Login with wrong password (should fail)")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('localhost', 50007))
        auth_msg = sock.recv(1024).decode('utf-8')
        
        login_msg = {'type': 'login', 'username': test_username, 'password': 'wrong_password'}
        sock.sendall((json.dumps(login_msg) + '\n').encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        result = json.loads(response)
        
        if not result.get('success'):
            print(f"  ✓ Correctly rejected: {result.get('message')}")
        else:
            print(f"  ✗ Should have failed but succeeded")
            return False
    finally:
        sock.close()
    
    time.sleep(0.2)
    
    # Test 5: Verify persistence - login again
    print(f"\n[TEST 5] Verify account persistence (re-login)")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('localhost', 50007))
        auth_msg = sock.recv(1024).decode('utf-8')
        
        login_msg = {'type': 'login', 'username': test_username, 'password': test_password}
        sock.sendall((json.dumps(login_msg) + '\n').encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        result = json.loads(response)
        
        if result.get('success'):
            print(f"  ✓ Account persisted and re-login successful")
        else:
            print(f"  ✗ Re-login failed: {result.get('message')}")
            return False
    finally:
        sock.close()
    
    # Test 6: Verify accounts.json
    print(f"\n[TEST 6] Verify accounts.json persistence")
    if os.path.exists('accounts.json'):
        with open('accounts.json', 'r') as f:
            accounts = json.load(f)
        if test_username in accounts:
            acc = accounts[test_username]
            print(f"  ✓ Account found in accounts.json")
            print(f"    - Username: {test_username}")
            print(f"    - Password hash: {acc['password_hash'][:16]}...")
            print(f"    - Created: {time.ctime(acc['created'])}")
        else:
            print(f"  ✗ Account not found in accounts.json")
            return False
    else:
        print(f"  ✗ accounts.json not found")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60)
    return True

if __name__ == '__main__':
    # Check if server is running
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 50007))
        sock.close()
        print("✓ Chat server is running on port 50007")
    except:
        print("✗ Chat server not running. Starting it...")
        subprocess.Popen(['python', 'chat_server.py'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        time.sleep(2)
    
    try:
        success = test_account_flow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
