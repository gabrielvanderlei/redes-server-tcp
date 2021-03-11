# redes-server-tcp
Servidor TCP desenvolvido com Python

## Requisitos
- Possuir respostas padrões
- Caso o retorno não seja 200, então uma tela personalizada deve ser mostrada
- O servidor deve ser capaz de retornar diversos tipos de arquivos
- Deve ser possível de transmitir arquivos grandes (usando lazy evaluating)
- Caso não exista um index.html em uma pasta, mostrar a lista de arquivos na pasta
- O servidor deve ler arquivos de uma pasta específica, e criar essa pasta caso ela não exista
- TCP obrigatório

## Respostas
- 200 OK: Requisição bem sucedida
- 400 Bad Request: Mensagem de requisição com erro de sintaxe
- 404 Not Found: Documento requisitado não encontrado
- 505 HTTP Verison Not Supported: Versão do HTTP não suportada

