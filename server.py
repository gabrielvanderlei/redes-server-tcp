from datetime import datetime
import socket
import mimetypes
import os

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8080

URL_DEFAULT_BASE = './default'
URL_SRC_BASE = './src'

URL_400 = URL_DEFAULT_BASE + '/400.html'
URL_404 = URL_DEFAULT_BASE + '/404.html'
URL_500 = URL_DEFAULT_BASE + '/500.html'
URL_501 = URL_DEFAULT_BASE + '/501.html'
URL_505 = URL_DEFAULT_BASE + '/505.html'

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((SERVER_HOST, SERVER_PORT))
serverSocket.listen(1)
print('Listening on port {} ...'.format(SERVER_PORT))

if not os.path.exists(URL_SRC_BASE):
    os.makedirs(URL_SRC_BASE)

# reading default pages
defaultFileContent = {
    400: (open(URL_400)).read(),
    404: (open(URL_404)).read(),
    500: (open(URL_500)).read(),
    501: (open(URL_501)).read(),
    505: (open(URL_505)).read()
}
    
messageCode = {
    200: "OK",
    400: "BAD REQUEST",
    404: "NOT FOUND",
    500: "INTERNAL SERVER ERROR",
    501: "NOT IMPLEMENTED",
    505: "HTTP VERSION NOT SUPPORTED"
}

def mountHTMLLink(href, name):
    return '<a href="{0}">{1}</a><br />'.format(href, name)

def listDirs(baseDir):
    htmlResponse = '<div class="dirLinks">'
    htmlResponse += '<h4>Abaixo está a listagem de arquivos disponíveis nesse diretório.</h4><br />'
    htmlResponse += '<h4>Diretório {0}</h4>'.format(baseDir)
    
    htmlResponse += '<table>'
    
    allDirInfo = os.walk(URL_SRC_BASE + baseDir)
    atualDirInfo = next(allDirInfo)
    
    path = atualDirInfo[0]
    subdirsList = atualDirInfo[1]
    files = atualDirInfo[2]
    
    if len(files) > 0 or len(subdirsList) > 0:
        htmlResponse += '<tr>'
        htmlResponse += '<td>Nome</td>'
        htmlResponse += '<td>Última modificação</td>'
        htmlResponse += '<td>Tamanho</td>'
        htmlResponse += '</tr>'
    else:
        htmlResponse += '<tr>'
        htmlResponse += '<td>Nenhum arquivo ou sub diretório encontrado</td>'
        htmlResponse += '</tr>'
    
    for subdir in subdirsList:
        subdirHref = baseDir + subdir
        subdirTitle = "/{0}".format(subdir)
        
        htmlResponse += '<tr>'
        htmlResponse += '<td>{0}</td>'.format(mountHTMLLink(subdirHref, subdirTitle))
        htmlResponse += '<td>{0}</td>'.format('')
        htmlResponse += '<td>{0}</td>'.format('')
        htmlResponse += '</tr>'
    
    for name in files:
        filePath  = os.path.join(path, name)
        size = os.path.getsize(filePath)
        lastModified = os.path.getmtime(filePath)
        fileHref = '{0}/{1}'.format(baseDir, name)
        
        htmlResponse += '<tr>'
        htmlResponse += '<td>{0}</td>'.format(mountHTMLLink(fileHref, name))
        htmlResponse += '<td>{0}</td>'.format(datetime.utcfromtimestamp(lastModified).strftime('%Y-%m-%d %H:%M:%S'))
        htmlResponse += '<td>{0}</td>'.format(size)
        htmlResponse += '</tr>'
            
    htmlResponse += '</table>'
    htmlResponse += '</div>'
    return htmlResponse

while True:
    clientConnection, clientAddress = serverSocket.accept()
    
    request = clientConnection.recv(1024).decode()
    print(request)
    
    linhas = request.strip().split('\r\n')
    linha1Colunas = linhas[0].split(' ')
    
    responseCode = 200
    mimeType = "text/html"
    isValidRequest = True
    method = 'GET'
    url = '/'
    versionType = 'HTTP/1.1'
    
    for linha in linhas[1:]:
        splittedLine = linha.split(':')
        isValidLine = ( splittedLine[0] and len(splittedLine[0].split(' ')) == 1 )
        if not isValidLine:
            isValidRequest = False
    
    if isValidRequest:
        method = linha1Colunas[0]
        url = linha1Colunas[1]
        versionType = linha1Colunas[2]
        
        if method != 'GET':
            responseCode = 501
        elif versionType != 'HTTP/1.1':
            responseCode = 505
        else:
            print('A requisicao possui suporte por esse servidor e a URL requisitada foi: {}'.format(url))
        
        try:
            try:
                fileURL = URL_SRC_BASE + url
                file = open(fileURL, "rb")
                mimeType = mimetypes.guess_type(fileURL);
            except FileNotFoundError:
                responseCode = 404
            except IsADirectoryError:
                if os.path.exists(URL_SRC_BASE + url + '/index.html'):
                    fileURL = URL_SRC_BASE + url + '/index.html'
                    file = open(fileURL, "rb")
                    mimeType = mimetypes.guess_type(fileURL);
                else:
                    responseCode = 404
                        
            
            if responseCode == 200:
                fileContents = file.read()
            else:
                fileContents = defaultFileContent[responseCode]
            
            if responseCode == 404:
                if os.path.exists(URL_SRC_BASE + url):
                    fileContents += listDirs(url)
        except:
            responseCode = 500
            fileContents = defaultFileContent[500]
    else:
        responseCode = 400
        fileContents = defaultFileContent[400]
    
    response = '{0} {1} {2} '.format(versionType, responseCode, messageCode[responseCode])
    response += '\n Content-Type: {0}'.format(mimeType[0])
    response += '\n\n'
    
    clientConnection.sendall(response.encode())
    
    if type(fileContents) is str:
        clientConnection.sendall(fileContents.encode())
    elif type(fileContents) is bytes:
        clientConnection.sendall(fileContents)
    
    clientConnection.close()

serverSocket.close()