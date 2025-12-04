import socket, json, time
HOST='127.0.0.1'
PORT=50007

def send_and_recv(messages):
    with socket.create_connection((HOST, PORT), timeout=3) as s:
        s.sendall((json.dumps({'type':'join','username':'tester'})+'\n').encode())
        time.sleep(0.1)
        for m in messages:
            s.sendall((json.dumps({'type':'msg','username':'tester','text':m})+'\n').encode())
            time.sleep(0.2)
        # read responses
        s.settimeout(1.0)
        try:
            data = b''
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
        except Exception:
            pass
        if data:
            for line in data.split(b'\n'):
                if not line: continue
                try:
                    print(json.loads(line.decode()))
                except Exception:
                    print('raw:', line)

if __name__=='__main__':
    send_and_recv(['Hello everyone!', 'This is damn test', 'You are an idiot'])
