import socket
import os

FLAGS = _ = None
DEBUG = False

FILES_DIR = __file__.replace('udp_server.py', 'files')

def get_file_list(directory):
    files = {}
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        if os.path.isfile(full_path):
            size = os.path.getsize(full_path)
            files[filename] = {'size': size, 'path': full_path}
    return files


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')
        
    print('Ready to file transfer')
    file_info = get_file_list(FILES_DIR)
    for fname, info in file_info.items():
        print(f"{fname}: {info}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))
    print(f'Listening on {sock}')
    
    while True:
        data, client = sock.recvfrom(2**16)
        data = data.decode('utf-8').strip()
        print(f'Received {data} from {client}')
        data = data.split(' ')
        
        if data[1] not in file_info:
            error_msg = "404 Not Found"
            sock.sendto(error_msg.encode('utf-8'), client)
            print(f"Sent error to {client}")
            continue
        
        elif data[0] == 'INFO':
            sock.sendto(f"{file_info[data[1]]['size']}".encode('utf-8'), client)
        
        elif data[0] == 'DOWNLOAD':
            with open(file_info[data]['path'], 'rb') as f:
                file_size = file_info[data]['size']
                remaining = file_size
                
                while remaining > 0:
                    read_size = min(FLAGS.mtu, remaining)
                    chunk = f.read(read_size)
                    if not chunk:
                        break
                    sock.sendto(chunk, client)
                    remaining -= len(chunk)

        
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
    help='The present debug message')
    parser.add_argument('--address', type=str, default='127.0.0.1',
    help='The address to serve service')
    parser.add_argument('--port', type=int, default=3034,
    help='The port to serve service')
    parser.add_argument('--mtu', type=int, default=1500,
    help='Max receive buffer size')
    
    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug
    main()