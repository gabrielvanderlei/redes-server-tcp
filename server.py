import socket

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 3000

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((SERVER_HOST, SERVER_PORT))
serverSocket.listen(1)
print('Listening on port {} ...'.format(SERVER_PORT))

while True:    
    clientConnection, clientAddress = serverSocket.accept()

    request = clientConnection.recv(1024).decode()
    print(request)
    
    linhas = request.strip().split('\r\n')

    for i, linha in enumerate(linhas):
        if i == 0:
            colunas = linha.split(' ')
            if colunas[0] != 'GET':
                raise Exception('501 Not Implemented')
            elif colunas[2] != 'HTTP/1.1':
                raise Exception('505 HTTP Version Not Supported')
            else:
                url = colunas[1]
                print('A requisicao possui suporte por esse servidor e a URL requisitada foi: {}'.format(url))
        break

    response = 'HTTP/1.1 200 OK\n\nHello World'
    clientConnection.sendall(response.encode())
    clientConnection.close()

serverSocket.close()