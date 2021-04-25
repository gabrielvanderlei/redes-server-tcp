import socket
import mimetypes
import os

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8080

URL_DEFAULT_BASE = './default'
URL_SRC_BASE = './src'

URL_404 = URL_DEFAULT_BASE + '/404.html'
URL_500 = URL_DEFAULT_BASE + '/500.html'

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((SERVER_HOST, SERVER_PORT))
serverSocket.listen(1)
print('Listening on port {} ...'.format(SERVER_PORT))

# reading default pages
fileNotFoundTemplate = open(URL_404)
fileNotFoundContent = fileNotFoundTemplate.read()

internalServerErrorTemplate = open(URL_500)
internalServerErrorFileContent = internalServerErrorTemplate.read()

messageCode = {
    200: "OK",
    404: "NOT FOUND",
    500: "INTERNAL SERVER ERROR"
}

def mountHTMLLink(href, name):
    return '<a href="{0}">{1}</a><br />'.format(href, name)

def listDirs(baseDir):
    htmlResponse = '<div class="dirLinks">'
    htmlResponse += '<h4>Abaixo está a listagem de arquivos disponíveis nesse diretório:</h4>'
    
    allDirInfo = os.walk(URL_SRC_BASE + baseDir)
    atualDirInfo = next(allDirInfo)
    
    #path = atualDirInfo[0]
    subdirsList = atualDirInfo[1]
    files = atualDirInfo[2]
    
    for subdir in subdirsList:
        subdirHref = baseDir + subdir
        subdirTitle = "/{0}".format(subdir)
        htmlResponse += mountHTMLLink(subdirHref, subdirTitle)
    
    for name in files:
        fileHref = '{0}/{1}'.format(baseDir, name)
        htmlResponse += mountHTMLLink(fileHref, name)
            
    htmlResponse += '</div>'
    return htmlResponse

while True:
    clientConnection, clientAddress = serverSocket.accept()
    
    request = clientConnection.recv(1024).decode()
    print(request)
    
    linhas = request.strip().split('\r\n')
    linha1Colunas = linhas[0].split(' ')
    
    method = linha1Colunas[0]
    url = linha1Colunas[1]
    versionType = linha1Colunas[2]

    if method != 'GET':
        raise Exception('501 Not Implemented')
    elif versionType != 'HTTP/1.1':
        raise Exception('505 HTTP Version Not Supported')
    else:
        print('A requisicao possui suporte por esse servidor e a URL requisitada foi: {}'.format(url))
        
    responseCode = 200
    mimeType = "text/html"
    
    try:
        try:
            fileURL = URL_SRC_BASE + url
            file = open(fileURL, "rb")
            mimeType = mimetypes.guess_type(fileURL);
        except FileNotFoundError:
            responseCode = 404
        except IsADirectoryError:
            responseCode = 404
        
        if responseCode == 200:
            fileContents = file.read()
        elif responseCode == 404:
            fileContents = fileNotFoundContent
            
            if os.path.exists(URL_SRC_BASE + url):
                fileContents += listDirs(url)
    except:
        responseCode = 500
        fileContents = internalServerErrorFileContent
    
    response = '{0} {1} {2} '.format(versionType, responseCode, messageCode[responseCode])
    
    # if type(fileContents) is bytes and mimeType[0] != 'text/html':
    #     fileSplitted = url.split('/')
    #     fileName = fileSplitted[len(fileSplitted) - 1]
    #     response += '\n Content-Disposition: attachment; filename={0};'.format(fileName)
    
    response += '\n Content-Type: {0}'.format(mimeType[0])
    response += '\n\n'
    
    clientConnection.sendall(response.encode())
    
    if type(fileContents) is str:
        clientConnection.sendall(fileContents.encode())
    elif type(fileContents) is bytes:
        clientConnection.sendall(fileContents)
    
    clientConnection.close()

serverSocket.close()