#!/usr/bin/env python3
"""
Simple chat server with moderation for the car-race project.
- Accepts TCP JSON lines from clients.
- Moderates messages: bullying terms -> ban; inappropriate terms -> warn + censor.
- Broadcasts messages to connected clients.

Run: python3 chat_server.py
"""
import socket
import threading
import json
import os
import time
import hashlib
from datetime import datetime, timedelta

HOST = '0.0.0.0'
PORT = 50007

# Account persistence
ACCOUNTS_FILE = 'accounts.json'

def hash_password(password):
    """Hash password with SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_accounts():
    """Load accounts from file"""
    try:
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_accounts(accounts):
    """Save accounts to file"""
    try:
        with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, indent=2)
    except Exception:
        pass

def register_account(username, password):
    """Register a new account. Returns (success, message)"""
    accounts = load_accounts()
    if username in accounts:
        return False, "Username already exists"
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 4:
        return False, "Password must be at least 4 characters"
    
    accounts[username] = {
        'password_hash': hash_password(password),
        'created': time.time()
    }
    save_accounts(accounts)
    return True, "Account created successfully"

def login_account(username, password):
    """Login an account. Returns (success, message)"""
    accounts = load_accounts()
    if username not in accounts:
        return False, "Username not found"
    
    stored_hash = accounts[username].get('password_hash', '')
    provided_hash = hash_password(password)
    
    if stored_hash != provided_hash:
        return False, "Incorrect password"
    
    return True, "Login successful"

# Load moderation config from file
CONFIG_FILE = 'moderation_config.json'
def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            return {
                'bullying_terms': set(cfg.get('bullying_terms', [])),
                'inappropriate_terms': set(cfg.get('inappropriate_terms', [])),
                'warning_threshold': cfg.get('warning_threshold', 3),
                'temp_ban_duration_minutes': cfg.get('temp_ban_duration_minutes', 60),
                'censor_mask': cfg.get('censor_mask', '***********')
            }
    except Exception as e:
        print(f"Warning: Could not load config: {e}. Using defaults.")
        return {
            'bullying_terms': {'idiot', 'stupid', 'kill', 'die', 'hate'},
            'inappropriate_terms': {'damn', 'crap'},
            'warning_threshold': 3,
            'temp_ban_duration_minutes': 60,
            'censor_mask': '***********'
        }

CONFIG = load_config()
BULLYING_TERMS = CONFIG['bullying_terms']
INAPPROPRIATE_TERMS = CONFIG['inappropriate_terms']
CENSOR_MASK = CONFIG['censor_mask']
WARNING_THRESHOLD = CONFIG['warning_threshold']
TEMP_BAN_DURATION = CONFIG['temp_ban_duration_minutes']

# Persistence files
BAN_FILE = 'banned_users.json'
WARN_FILE = 'warnings.json'

clients = {}  # conn -> {'addr':..., 'username':...}
clients_lock = threading.Lock()

# Load persisted bans and warnings with expiration
def load_persistent_set(path):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return set(json.load(f))
    except Exception:
        pass
    return set()

def load_persistent_dict(path):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def load_bans_with_expiry():
    """Load bans, returns {'user': timestamp or None}. None = permanent."""
    try:
        if os.path.exists(BAN_FILE):
            with open(BAN_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def is_banned(username):
    """Check if user is currently banned (including expired bans)."""
    if username not in banned_users:
        return False
    exp_time = banned_users[username]
    if exp_time is None:  # permanent ban
        return True
    # temp ban: check if expired
    if time.time() < exp_time:
        return True
    # expired, remove it
    del banned_users[username]
    save_bans()
    return False

def load_warnings():
    """Load warning counts from file"""
    try:
        if os.path.exists(WARN_FILE):
            with open(WARN_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_warnings(warnings):
    """Save warning counts to file"""
    try:
        with open(WARN_FILE, 'w', encoding='utf-8') as f:
            json.dump(warnings, f)
    except Exception:
        pass

banned_users = load_bans_with_expiry()  # {'user': None or timestamp}
warning_counts = load_warnings()

def save_bans_with_expiry():
    try:
        with open(BAN_FILE, 'w', encoding='utf-8') as f:
            json.dump(banned_users, f)
    except Exception:
        pass

def save_bans():
    save_bans_with_expiry()


def contains_any(text, terms):
    words = [w.strip(".,!?:;\"'()[]{}<>\n\r").lower() for w in text.split()]
    return any(w in terms for w in words)


def censor_text(text, terms):
    # Replace offending words by the fixed mask (preserving punctuation loosely)
    parts = text.split()
    for i, w in enumerate(parts):
        cleaned = w.strip(".,!?:;\"'()[]{}<>\n\r").lower()
        if cleaned in terms:
            parts[i] = CENSOR_MASK
    return ' '.join(parts)


def broadcast(msg_obj, exclude_conn=None):
    data = (json.dumps(msg_obj) + "\n").encode('utf-8')
    with clients_lock:
        for conn in list(clients.keys()):
            if conn is exclude_conn:
                continue
            try:
                conn.sendall(data)
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass
                if conn in clients:
                    del clients[conn]


def handle_client(conn, addr):
    authenticated_user = None
    with conn:
        try:
            # Send auth_required message immediately
            conn.sendall(json.dumps({'type': 'auth_required'}).encode('utf-8') + b'\n')
            
            buf = b''
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buf += chunk
                while b'\n' in buf:
                    line, buf = buf.split(b'\n', 1)
                    try:
                        msg = json.loads(line.decode('utf-8'))
                    except Exception:
                        continue

                    mtype = msg.get('type')
                    
                    # Handle registration
                    if mtype == 'register':
                        username = msg.get('username', '').strip()
                        password = msg.get('password', '')
                        success, auth_msg = register_account(username, password)
                        if success:
                            authenticated_user = username
                            try:
                                conn.sendall(json.dumps({'type': 'auth_response', 'success': True, 'message': 'Account created'}).encode('utf-8') + b'\n')
                            except Exception:
                                pass
                        else:
                            try:
                                conn.sendall(json.dumps({'type': 'auth_response', 'success': False, 'message': auth_msg}).encode('utf-8') + b'\n')
                            except Exception:
                                pass
                        continue
                    
                    # Handle login
                    elif mtype == 'login':
                        username = msg.get('username', '').strip()
                        password = msg.get('password', '')
                        success, auth_msg = login_account(username, password)
                        if success:
                            authenticated_user = username
                            try:
                                conn.sendall(json.dumps({'type': 'auth_response', 'success': True, 'message': 'Logged in'}).encode('utf-8') + b'\n')
                            except Exception:
                                pass
                        else:
                            try:
                                conn.sendall(json.dumps({'type': 'auth_response', 'success': False, 'message': auth_msg}).encode('utf-8') + b'\n')
                            except Exception:
                                pass
                        continue
                    
                    # All other messages require authentication
                    if not authenticated_user:
                        try:
                            conn.sendall(json.dumps({'type': 'error', 'message': 'Must authenticate first'}).encode('utf-8') + b'\n')
                        except Exception:
                            pass
                        continue
                    
                    # Now handle authenticated messages
                    if mtype == 'join':
                        username = authenticated_user
                        # If user is banned, immediately disconnect
                        if is_banned(username):
                            try:
                                conn.sendall(json.dumps({'type': 'system', 'text': 'You are banned.'}).encode('utf-8') + b'\n')
                            except Exception:
                                pass
                            break
                        broadcast({'type': 'system', 'text': f"{username} joined the chat."}, exclude_conn=None)

                    elif mtype == 'admin':
                        # Admin commands: ban, unban, list_bans, clear_warnings, temp_ban
                        username = authenticated_user
                        command = msg.get('command', '')
                        target = msg.get('target', '')
                        
                        if command == 'ban':
                            # Permanent ban
                            banned_users[target] = None
                            save_bans()
                            broadcast({'type': 'system', 'text': f"[ADMIN] {target} was permanently banned by {username}."})
                        elif command == 'unban':
                            if target in banned_users:
                                del banned_users[target]
                                save_bans()
                            broadcast({'type': 'system', 'text': f"[ADMIN] {target} was unbanned by {username}."})
                        elif command == 'temp_ban':
                            # Temp ban for X minutes
                            exp_time = time.time() + (TEMP_BAN_DURATION * 60)
                            banned_users[target] = exp_time
                            save_bans()
                            broadcast({'type': 'system', 'text': f"[ADMIN] {target} was temp-banned for {TEMP_BAN_DURATION}min by {username}."})
                        elif command == 'list_bans':
                            # Send ban list to requester (future: auth check)
                            bans_list = []
                            now = time.time()
                            for user, exp in banned_users.items():
                                if exp is None:
                                    bans_list.append(f"{user} (permanent)")
                                else:
                                    remaining = max(0, (exp - now) / 60)
                                    bans_list.append(f"{user} ({remaining:.1f}min remaining)")
                            try:
                                conn.sendall(json.dumps({'type': 'system', 'text': f"Bans: {', '.join(bans_list) if bans_list else 'none'}"}).encode('utf-8') + b'\n')
                            except Exception:
                                pass
                        elif command == 'clear_warnings':
                            if target in warning_counts:
                                del warning_counts[target]
                                save_warnings()
                            broadcast({'type': 'system', 'text': f"[ADMIN] Warnings for {target} cleared by {username}."})
                        elif command == 'list_warnings':
                            warns = ', '.join([f"{u}:{c}" for u, c in warning_counts.items()]) if warning_counts else 'none'
                            try:
                                conn.sendall(json.dumps({'type': 'system', 'text': f"Warnings: {warns}"}).encode('utf-8') + b'\n')
                            except Exception:
                                pass

                    elif mtype == 'msg':
                        username = authenticated_user
                        text = msg.get('text', '')

                        # Check bullying terms -> ban
                        if contains_any(text, BULLYING_TERMS):
                            # Ban the user
                            banned_users[username] = None  # permanent
                            save_bans()
                            # inform and disconnect
                            try:
                                conn.sendall(json.dumps({'type': 'system', 'text': 'You have been banned for bullying.'}).encode('utf-8') + b'\n')
                            except Exception:
                                pass
                            break

                        # Check inappropriate terms -> warn + censor
                        if contains_any(text, INAPPROPRIATE_TERMS):
                            # increment warning count
                            cnt = int(warning_counts.get(username, 0)) + 1
                            warning_counts[username] = cnt
                            save_warnings()
                            censored = censor_text(text, INAPPROPRIATE_TERMS)
                            # send warning to sender
                            try:
                                conn.sendall(json.dumps({'type': 'warning', 'text': f'Your message contained inappropriate language and was censored. Warnings: {cnt}/{WARNING_THRESHOLD}'}).encode('utf-8') + b'\n')
                            except Exception:
                                pass
                            # if exceeded threshold, ban
                            if cnt >= WARNING_THRESHOLD:
                                banned_users[username] = None  # permanent
                                save_bans()
                                try:
                                    conn.sendall(json.dumps({'type': 'system', 'text': 'You have been banned due to repeated inappropriate language.'}).encode('utf-8') + b'\n')
                                except Exception:
                                    pass
                                broadcast({'type': 'system', 'text': f"{username} was banned for repeated inappropriate language."}, exclude_conn=None)
                                break
                            # broadcast censored message
                            broadcast({'type': 'chat', 'username': username, 'text': censored}, exclude_conn=None)
                        else:
                            broadcast({'type': 'chat', 'username': username, 'text': text}, exclude_conn=None)
        
        except Exception as e:
            print(f"Error handling {addr}: {e}")
        
        finally:
            if authenticated_user:
                broadcast({'type': 'system', 'text': f"{authenticated_user} left the chat."}, exclude_conn=None)


def run_server():
    print(f"Starting chat server on {HOST}:{PORT}")
    print(f"Config loaded: {len(BULLYING_TERMS)} bullying terms, {len(INAPPROPRIATE_TERMS)} inappropriate terms")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()


if __name__ == '__main__':
    run_server()
