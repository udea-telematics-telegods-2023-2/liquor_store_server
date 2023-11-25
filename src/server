import logging
from rsa import key, encrypt, decrypt, newkeys
from socketserver import ForkingTCPServer, BaseRequestHandler
from socketserver import UDPServer, BaseRequestHandler
from src.liquor import Store
from sys import argv, exit
import json
from socket import AF_INET, SOCK_DGRAM, socket
class User_store:
    #se verificará si hay un usuario conectado
    #en este caso name tendrá que ser el uuid
    def __init__(self, name):
        self.name = name
        self.conect = False
    #si el usuario está conectado se retornará el nombre de este para luego 
    #enviarlo al banco
    def conectar(self):
        print(f"{self.name} se ha conectado.")
        self.conect = True
        return self.name
    def disconect(self):
        print(f"{self.name} se ha desconectado.")
        self.conect = False
    #consultar estado de conexión:
    def is_conect(self):
        return self.conect

    def show_list(self, liquor_list):
        if self.conect:           
            print(f"Lista de licores:\n{liquor_list}")
    def chose_one(self, liquor_list, opcion):
        if self.is_conect():
            try:
                opcion = int(opcion)
                liquor_list2 = json.loads(liquor_list)
                if 1 <= opcion <= len(liquor_list2):
                    print(f"{self.name} seleccionó el licor: {liquor_list2[opcion - 1]}")
                else:
                    print("No valid opcion.")
            except ValueError:
                print("Por favor, ingrese un número válido.")
    
class LiquorDelivery:
    def __init__(self, user_name):
        self.user_name = user_name
    def get_virtual_liquor(self, liquor_name):
        # Lógica para obtener el licor virtual correspondiente al nombre
        return f"Virtual {liquor_name}"
    def deliver_liquor(self, liquor_name):
        # Simular la validación del pago
        payment_validation = self.validate_payment()
        if payment_validation == "OK":
            # Entregar el licor virtual al usuario
            virtual_liquor = self.get_virtual_liquor(liquor_name)
            print(f"Licor entregado a {self.user_name}: {virtual_liquor}")
            return virtual_liquor
        else:
            print(f"Error en la validación del pago: {payment_validation_result}")
            return None
    def validate_payment(self):
        # confirmación "OK" desde el servidor del banco
        return "OK"
    def get_virtual_liquor(self, liquor_name):
        # obtener el licor virtual correspondiente al nombre
        return f"Virtual {liquor_name}"
class conection_bank:
    def bank_conection_server(self, mensaje):
        #dirección del servidor del banco
        server_bank_direction = ("127.0.0.0", 5555)
        #UDP socket
        with socket(AF_INET, SOCK_DGRAM) as udp_socket:
            udp_socket.sendto(mensaje.encode("utf-8"), server_bank_direction)
            print("Mensaje enviado al servidor del banco")

            response, _ = udp_socket.recvfrom(1024)
            print("Respuesta del servidor del banco:", response.decode("utf-8"))

            if response.decode("utf-8") == "OK":
                print("La transacción fue exitosa. Entregar el licor virtual al usuario.")
                #tomemos a Username como el uuid
                user_name = "NombreUsuario"  # Reemplaza con el nombre de usuario real
                liquor_name = "NombreLicor"  # Reemplaza con el nombre del licor real
                liquor_delivery = LiquorDelivery(user_name)
                liquor_delivery.deliver_liquor(liquor_name)
                
class MyHandler(BaseRequestHandler):
    def handle(self):
        print("Connection from ", str(self.client_address))
        data, conn = self.request
        decoded_data = data.decode("utf-8")

        if decoded_data.startswith("CONNECT"):
            # Obtener el UUID del usuario desde el comando CONNECT
            _, user_uuid = decoded_data.split()
            # Aquí le pasamos a User_Store el uuid del cliente que se conectó
            connected_user = User_store(user_uuid)
            # Aquí verificamos si está conectado 
            connected_user.conectar()
            # Desplego la lista
            store = Store()
            _, liquor_list = store.list()
            # Se envía la lista al cliente
            conn.sendall(json.dumps(liquor_list).encode("utf-8"))
            
            # Se recibe la elección del cliente
            user_choice = conn.recv(4096).decode("utf-8")                              
            # Obtener la opción del usuario y realizar la elección
            _, option = user_choice.split()
            connected_user.chose_one(liquor_list, option)
            
            # Obtener el nombre del licor seleccionado
            selected_liquor_name = liquor_list[int(option) - 1]
            
            # Obtener el número de puerto del socket
            server_port = conn.getsockname()[1]
            print(f"El número de puerto es: {server_port}")

        else:
            conn.sendall("Comando no reconocido".encode("utf-8"))



    
