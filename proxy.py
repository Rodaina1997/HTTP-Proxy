import sys
import os
import enum
import re
import socket
from _thread import *
import threading
from sys import argv
true=1
lock = threading.Lock()
my_dict=dict()

class HttpRequestInfo(object):
    """
    Represents a HTTP request information
    Since you'll need to standardize all requests you get
    as specified by the document, after you parse the
    request from the TCP packet put the information you
    get in this object.
    To send the request to the remote server, call to_http_string
    on this object, convert that string to bytes then send it in
    the socket.
    client_address_info: address of the client;
    the client of the proxy, which sent the HTTP request.
    requested_host: the requested website, the remote website
    we want to visit.
    requested_port: port of the webserver we want to visit.
    requested_path: path of the requested resource, without
    including the website name.
    NOTE: you need to implement to_http_string() for this class.
    """

    def __init__(self, client_info, method: str, requested_host: str,
                 requested_port: int,
                 requested_path: str,
                 headers: list):
        self.method = method
        self.client_address_info = client_info
        self.requested_host = requested_host
        self.requested_port = requested_port
        self.requested_path = requested_path
        # Headers will be represented as a list of lists
        # for example ["Host", "www.google.com"]
        # if you get a header as:
        # "Host: www.google.com:80"
        # convert it to ["Host", "www.google.com"] note that the
        # port is removed (because it goes into the request_port variable)
        self.headers = headers

    def to_http_string(self):
        """
        Convert the HTTP request/response
        to a valid HTTP string.
        As the protocol specifies:
        [request_line]\r\n
        [header]\r\n
        [headers..]\r\n
        \r\n
        (just join the already existing fields by \r\n)
        You still need to convert this string
        to byte array before sending it to the socket,
        keeping it as a string in this stage is to ease
        debugging and testing.
        """
        http_list = []
        headers_string = ""
        http_list.append(self.method)
        #http_list.append('/')
        http_list.append(self.requested_path)
        http_list.append('HTTP/1.0')
        http_string = ' '.join([str(elem) for elem in http_list])
        http_string += '\r\n'
        for i in self.headers:
            header_string = ': '.join([str(elem) for elem in i])
            headers_string += header_string
            headers_string += '\r\n'
        http_string += headers_string
        http_string += '\r\n'
        print("*" * 50)
        print("[to_http_string] Implement me!")
        print("*" * 50)
        return http_string

    def to_byte_array(self, http_string):
        """
        Converts an HTTP string to a byte array.
        """
        return bytes(http_string, "UTF-8")

    def display(self):
        print(f"Client:", self.client_address_info)
        print(f"Method:", self.method)
        print(f"Host:", self.requested_host)
        print(f"Port:", self.requested_port)
        stringified = [": ".join([k, v]) for (k, v) in self.headers]
        print("Headers:\n", "\n".join(stringified))


class HttpErrorResponse(object):
    """
    Represents a proxy-error-response.
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def to_http_string(self):
        """ Same as above """
        http_string = ''
        http_string += self.message
        http_string += self.code
        http_string += 'response'
        return http_string

    def to_byte_array(self, http_string):
        """
        Converts an HTTP string to a byte array.
        """
        return bytes(http_string, "UTF-8")

    def display(self):
        print(self.to_http_string())


class HttpRequestState(enum.Enum):
    """
    The values here have nothing to do with
    response values i.e. 400, 502, ..etc.
    Leave this as is, feel free to add yours.
    """
    INVALID_INPUT = 0
    NOT_SUPPORTED = 1
    GOOD = 2
    PLACEHOLDER = -1


def entry_point(conn):
    """
    Entry point, start your code here.
    Please don't delete this function,
    but feel free to modify the code
    inside it.
    """

    serv2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global http_raw_data
    http_raw_data = ''
    response = bytearray()
    while True:
        data = conn.recv(4096)
        if not data:
            print('Bye')
            lock.release()
            break
        if data in my_dict :
            response=my_dict.get(data)
            break
        http_raw_data += data.decode("utf-8")
        if (http_raw_data.find('\r\n\r\n') != -1):
            parsed_http_raw_data,validity=http_request_pipeline(source_addr, http_raw_data)
                #host_string=parsed_string.split(":")[1]
                #host=host_string.strip()
            if (validity == HttpRequestState.GOOD):
                object2 = parse_http_request(source_addr, http_raw_data)
                host=object2.requested_host
                port = object2.requested_port
                portno=int(port)
                ip=socket.gethostbyname(host)
                    #server_address = (ip,port)
                serv2.connect((ip,portno))
                serv2.send(parsed_http_raw_data)
                print("Waiting to receive: ")

                while true:
                    Data=serv2.recv(4096)
                    if not Data:
                        break
                    response+=Data
                print('received {!r}'.format(response))
                my_dict[data] = response
                serv2.close()
                print('web server disconnected')
            else:
                response =parsed_http_raw_data

            conn.sendall(response)
            print('response is sent to client')
            break

    conn.close()
    print('client disconnected')
    lock.release()
    # connections automatically.
    print("*" * 50)
    print("[entry_point] Implement me!")
    print("*" * 50)
    return None


def setup_sockets(proxy_port_number):
    """
    Socket logic MUST NOT be written in the any
    class. Classes know nothing about the sockets.
    But feel free to add your own classes/functions.
    Feel free to delete this function.
    """
    print("Starting HTTP proxy on port:", proxy_port_number)
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(("127.0.0.1",proxy_port_number))
    # when calling socket.listen() pass a number
    # that's larger than 10 to avoid rejecting
    serv.listen(15)
    global source_addr
    while True:
        conn, source_addr = serv.accept()
        print("Connection from {} has been established!".format(source_addr))
        http_raw_data = ''
        lock.acquire()
        print('Connected to :', source_addr[0], ':', source_addr[1])
        start_new_thread(entry_point, (conn,))
    print("*" * 50)
    print("[setup_sockets] Implement me!")
    print("*" * 50)



def parse_sanitize(http_raw_data):
    headers = []
    new = http_raw_data.split('\r\n')
    for i in new:
        if (i == ''):
            new.remove(i)
    method = new[0].split()[0]
    port_num = "80"
    path = '/'
    host_flag = False

    if (http_raw_data.find("www") != -1):
        end = http_raw_data.find('.com')
        url = http_raw_data[http_raw_data.find('www'): end + 4]
        host_flag = True

    if (host_flag == False):
        if re.search(r"(?<=http://)(\S+)(?=:)", http_raw_data):
            url = re.search(r"(?<=http://)(\S+)(?=:)", http_raw_data).group(1)
            path = new[0].split()[1]
            host_flag = True
            # print('Regex URL : ', url)
        elif (http_raw_data.find("://") != -1):
            end_n = http_raw_data.find('://')
            url = http_raw_data[(end_n + 3): http_raw_data.find('/ ')]
            path = new[0].split()[1]
            host_flag = True

    if (http_raw_data.find(".html") != -1):
        end = http_raw_data.find('.html')
        path = http_raw_data[http_raw_data.find('/'): end + 5]

    if (http_raw_data.find("Host") != -1) and (host_flag == False):
        url = new[1].split()[1]
        host_flag = True

    if (host_flag == True):
        header = ['Host', url]
        headers.append(header)

    if re.search(r'\d', http_raw_data):
        temp = re.findall(r'\d+', http_raw_data)
        res = list(map(int, temp))
        for i in range(0, len(res)):
            if (i == 1) or (i == 0):
                res.remove(i)
        new_port_num = ''.join([str(elem) for elem in res])
        if new_port_num:
            port_num = new_port_num

    if (len(new) > 3):
        header = new[-2].split(':')
        headers.append(header)

    return method, url, port_num,path, headers


def http_request_pipeline(source_addr, http_raw_data):
    """
    HTTP request processing pipeline.
    - Validates the given HTTP request and returns
      an error if an invalid request was given.
    - Parses it
    - Returns a sanitized HttpRequestInfo
    returns:
     HttpRequestInfo if the request was parsed correctly.
     HttpErrorResponse if the request was invalid.
    Please don't remove this function, but feel
    free to change its content
    """
    # Validate, sanitize, return Http object.
    validity = check_http_request_validity(http_raw_data)

    # Return error if needed, then:
    # parse_http_request()
    # sanitize_http_request()

    #http_raw_data_string=''

    if (validity == HttpRequestState.GOOD):
        # Parse HTTP request
        parsed_http_raw_data = parse_http_request(source_addr, http_raw_data)
        sanitize_http_request(parsed_http_raw_data)
        parsed_http_raw_data_string = parsed_http_raw_data.to_http_string()
        http_response_bytes=parsed_http_raw_data.to_byte_array(parsed_http_raw_data_string)

        #sanitize_http_request(request_info: HttpRequestInfo)
    elif (validity == HttpRequestState.NOT_SUPPORTED):
        http_response_error = HttpErrorResponse('(501)',"Not Implemented")
        #http_raw_data_string += http_raw_data
        http_raw_data_string = http_response_error.to_http_string()
        http_response_bytes=http_response_error.to_byte_array(http_raw_data_string)

    elif (validity == HttpRequestState.INVALID_INPUT):
        http_response_error=HttpErrorResponse('(400)',"Bad Request")
        #http_raw_data_string += http_raw_data
        http_raw_data_string = http_response_error.to_http_string()
        http_response_bytes=http_response_error.to_byte_array(http_raw_data_string)


    print("*" * 50)
    print("[http_request_pipeline] Implement me!")
    print("*" * 50)
    return http_response_bytes,validity


def parse_http_request(source_addr, http_raw_data):
    """
    This function parses a "valid" HTTP request into an HttpRequestInfo
    object.
    """
    print("*" * 50)
    print("[parse_http_request] Implement me!")
    print("*" * 50)
    method, url, port_num, path, headers = parse_sanitize(http_raw_data)
    # Replace this line with the correct values.
    ret = HttpRequestInfo(source_addr, method, url, port_num,path, headers)
    return ret


def check_http_request_validity(http_raw_data) -> HttpRequestState:
    """
    Checks if an HTTP request is valid
    returns:
    One of values in HttpRequestState
    """
    print("*" * 50)
    print("[check_http_request_validity] Implement me!")
    print("*" * 50)
    new = http_raw_data.split('\r\n')
    valid=True
    flag = True
    for i in new:
        if (i == ''):
            new.remove(i)
    if (new[-1] == ''):
        new.pop(-1)

    if (len(new) > 1) and (http_raw_data.find(":") == -1):
        print('Bad header [no colon, no value]')
        valid = False
        flag = False
        return HttpRequestState.INVALID_INPUT

    elif (http_raw_data.find("Host") == -1):
        path_reg = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+] |[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', http_raw_data)
        if not path_reg:
            if (http_raw_data.find("www") == -1) and (http_raw_data.find('.com') == -1):
                print("Error :Relative path with no host header")
                flag = False
                valid = False
                return HttpRequestState.INVALID_INPUT

    elif (http_raw_data.find("HTTP/1.0") == -1) :
        print('No HTTP Version')
        flag = False
        valid = False
        return HttpRequestState.INVALID_INPUT

    method = new[0].split()[0]
    available_methods = ['GET', 'HEAD', 'POST', 'PUT']

    if (flag == True):
        if method in available_methods:
            if (method != 'GET'):
                valid = False
                print('Not Implemented Method')
                return HttpRequestState.NOT_SUPPORTED
        else:
            valid = False
            print('Invalid Method')
            return HttpRequestState.INVALID_INPUT

    if (valid == True):
        return HttpRequestState.GOOD

    # return HttpRequestState.GOOD (for example)
    return HttpRequestState.PLACEHOLDER


def sanitize_http_request(request_info: HttpRequestInfo):
    """
    Puts an HTTP request on the sanitized (standard) form
    by modifying the input request_info object.
    for example, expand a full URL to relative path + Host header.
    returns:
    nothing, but modifies the input object
    """
    print("*" * 50)
    print("[sanitize_http_request] Implement me!")
    print("*" * 50)
    method, url, port_num, path, headers = parse_sanitize(http_raw_data)
    request_info.method = method
    request_info.requested_host = url
    request_info.requested_port = port_num
    request_info.requested_path = path
    request_info.headers = headers


#######################################
# Leave the code below as is.
#######################################


def get_arg(param_index, default=None):
    """
        Gets a command line argument by index (note: index starts from 1)
        If the argument is not supplies, it tries to use a default value.
        If a default value isn't supplied, an error message is printed
        and terminates the program.
    """
    try:
        return sys.argv[param_index]
    except IndexError as e:
        if default:
            return default
        else:
            print(e)
            print(
                f"[FATAL] The comand-line argument #[{param_index}] is missing")
            exit(-1)    # Program execution failed.


def check_file_name():
    """
    Checks if this file has a valid name for *submission*
    leave this function and as and don't use it. it's just
    to notify you if you're submitting a file with a correct
    name.
    """
    script_name = os.path.basename(__file__)
    import re
    matches = re.findall(r"(\d{4}_){,2}lab2\.py", script_name)
    if not matches:
        print(f"[WARN] File name is invalid [{script_name}]")
    else:
        print(f"[LOG] File name is correct.")


def main():
    """
    Please leave the code in this function as is.
    To add code that uses sockets, feel free to add functions
    above main and outside the classes.
    """
    print("\n\n")
    print("*" * 50)
    print(f"[LOG] Printing command line arguments [{', '.join(sys.argv)}]")
    check_file_name()
    print("*" * 50)
    #global proxy_port_number
    python_file,proxy_port_number = argv
    # This argument is optional, defaults to 18888
    #proxy_port_number = get_arg(1, 2233)
    setup_sockets(int(proxy_port_number))



if __name__ == "__main__":
    main()
