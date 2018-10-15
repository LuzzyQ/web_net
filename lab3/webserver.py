import filetype
import asyncio
import os
from parse_header import HTTPHeader
content=[]
ok=[
    b'HTTP/1.0 200 OK\r\n',
    b'Content-Type:text/html; charset=utf-8\r\n',
    b'Connection: close\r\n',
    b'\r\n']
err404=[
    b'HTTP/1.0 404 OK\r\n',
    b'Content-Type:text/html; charset=utf-8\r\n',
    b'Connection: close\r\n',
    b'\r\n',
    b'<html><body>404 Not Found<body></html>\r\n',
    b'\r\n'
]
err405=[
    b'HTTP/1.0 405 OK\r\n',
    b'Content-Type:text/html; charset=utf-8\r\n',
    b'Connection: close\r\n',
    b'\r\n',
    b'<html><body>405 Method Not Allowed<body></html>\r\n',
    b'\r\n'
]
def mimetype(path):
    kind = filetype.guess(path)
    if kind is None:
        return 'application/octet-stream'
    return kind.mime

def check(list,name):
    for x in list:
        if name==x:
            return True
    return False

def add_head(path):
    content.append(b'HTTP/1.0 200 OK\r\n')
    content.append(b'Content-Type:'+mimetype(path).encode()+b'; charset=utf-8\r\n')
    content.append(b'Connection: close\r\n')
    content.append(b'\r\n')
    return content
def add_dir_list(path):
    global content
    if path=='/':
        dirs=os.listdir()
    else:
        dirs=os.listdir('./'+path)
    #print(dirs)
    content+=ok
    text=r'<html><head><title>Index of ./'+path+r'</title></head>'
    content.append(text.encode())
    content+=[b'<body bgcolor="white">',b'<h1>Index of ./'+path.encode()+b'</h1><hr>', b'<pre>' ]
    content.append(b'<a href="../">../</a>\r\n')
    #print(content)
    for x in dirs:        
        text=r'<a href="'+x+r'">'+x+'</a>\r\n'
        #print(text)
        content.append(text.encode())
    content+=[b'</pre>',b'<hr>',b'<body><html>']
    return content
def openfile(writer,path):
    file=open(path)
    #head lost
    #print(file.read())
    writer.writelines(add_head(path))
    #console(file.read())
    writer.write(file.read().encode())
    

def service(HTTPHeader,writer):
    if HTTPHeader.get('method') !="GET" and HTTPHeader.get('method') !="HEAD":
        writer.writelines(err405)
    path = HTTPHeader.get('path').strip()
    #print(path[1:])
    #print(os.listdir())
    del content[:]
    if path=='/':
        writer.drain()
        writer.writelines(add_dir_list(path))
        #writer.writelines(ok+dir)#need add dir list

    elif(not check(os.listdir(),path[1:])):
        raise FileNotFoundError
    elif(os.path.isfile(path[1:])):
        openfile(writer,'.'+path)
    else:
        #print(path)
        writer.drain()
        writer.writelines(add_dir_list(path[1:]))
async def dispatch(reader, writer):
    header = HTTPHeader()
    while True:
        data = await reader.readline()
        message = data.decode()
        header.parse_header(message)
        if data == b'\r\n':
            break
    path = header.get('path').strip()
    print(path)
    #print(os.path.isfile(path[1:]))#check is file or dir
    try:
        service(header,writer)
    except:
        writer.writelines(err404)
    await writer.drain()
    writer.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch, '127.0.0.1', 8080, loop=loop)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


