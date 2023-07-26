from network import WLAN, STA_IF

def wifi_station_connector_with_ssid_and_password(ssid, password):
    def wifi_station_connection_tester(station):
        wifi_station_connection_test = station.isconnected()
        return wifi_station_connection_test
    station = WLAN(STA_IF)
    station.active(True)
    station.connect(ssid, password)
    while wifi_station_connection_tester(station) == False:
        pass
    print('Connection successful')
    print(station.ifconfig())
    return station

# try:
#   from usocket import socket, AF_INET, SOCK_STREAM
# except:
from socket import socket, AF_INET, SOCK_STREAM 
def socket_connector_with_port_max_listenable_and_host(port, max_listenable, host = ''):
    socket_connection = socket(AF_INET, SOCK_STREAM)
    socket_connection.bind((host, port))
    socket_connection.listen(max_listenable)
    return socket_connection

def socket_accepted_connection(socket_connection):
    connection, address = socket_connection.accept()
    print('Got a connection from %s' % str(address))
    return connection

def socket_request_receiver(connection, request_size = 1024):
    request = connection.recv(request_size)
    request = str(request)
    print('Content = %s' % request)
    return request

def web_page_loader(file_address, replace_string, locker_state):
    with open(file_address, 'r') as file:
        html = file.read().replace(replace_string, locker_state)
        return html

def socket_response_sender_by_conn(connection, response):
    connection.send('HTTP/1.1 200 OK\n')
    connection.send('Content-Type: text/html\n')
    connection.send('Connection: close\n\n')
    connection.sendall(response)
    connection.close()


from machine import Pin, PWM
def init_locker(pin_id_number = 25, motor_duty = 40, motor_freq = 50, locker_status = "OFF"):
    #inicializa fechadura
    pin = Pin(pin_id_number, Pin.OUT)
    motor = PWM(pin, motor_freq)
    motor.duty(motor_duty)
    locker_state = locker_status
    return locker_state, motor

def open_locker_request(request):
    locker_on = request.find('/?locker=on')
    return locker_on

def close_locker_request(request):
    locker_off = request.find('/?locker=off')
    return locker_off

def open_locker(motor):
    print('LOCKER ON')
    motor.duty(110)
    locker_state = "ON"
    return locker_state
    
def close_locker(motor):
    global locker_state
    print('LOCKER OFF')
    motor.duty(40)
    locker_state = "OFF"
    return locker_state
