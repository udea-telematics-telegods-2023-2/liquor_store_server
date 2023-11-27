#!/usr/bin/env python
import json
import logging
from socket import AF_INET, SOCK_DGRAM, socket
from socketserver import ForkingTCPServer, ForkingUDPServer, BaseRequestHandler
from src.liquor import Store
from sys import argv, exit
from random import randint
from threading import Thread


class Formatter(logging.Formatter):
    """
    Custom log formatter for a more 'pichuki' log output.

    Attributes:
        FORMATS (dict): A mapping of log levels to their respective formats.
            The formats include the log level, timestamp, and log message.
        DATEFMT (str): The date format for the timestamp.

    Methods:
        format(record): Formats a log record into a string.
    """

    FORMATS = {
        logging.DEBUG: "[DEBUG] %(asctime)s - %(message)s",
        logging.INFO: "[INFO]  %(asctime)s - %(message)s",
        logging.WARNING: "[WARN]  %(asctime)s - %(message)s",
        logging.ERROR: "[ERROR] %(asctime)s - %(message)s",
        logging.CRITICAL: "[CRIT]  %(asctime)s - %(message)s",
    }

    DATEFMT = "%d-%m-%Y %H:%M:%S"

    def format(self, record) -> str:
        """
        Formats a log record into a string.

        Args:
            record (LogRecord): The log record to be formatted.

        Returns:
            str: The formatted log message.

        Notes:
            This method overrides the format method in the logging.Formatter class.
        """
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format, datefmt=self.DATEFMT)
        return formatter.format(record)

class Server:
    # se verificará si hay un usuario conectado
    # en este caso name tendrá que ser el uuid
    def __init__(self, name):
        self.name = name
        self.conect = False

    # si el usuario está conectado se retornará el nombre de este para luego
    # enviarlo al banco
    def conectar(self):
        print(f"{self.name} se ha conectado.")
        self.conect = True
        return self.name

    def disconect(self):
        print(f"{self.name} se ha desconectado.")
        self.conect = False

    # consultar estado de conexión:
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
                    print(
                        f"{self.name} seleccionó el licor: {liquor_list2[opcion - 1]}"
                    )
                else:
                    print("No valid opcion.")
            except ValueError:
                print("Por favor, ingrese un número válido.")
                
    def __init__(self, user_name):
        self.user_name = user_name

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
    def bank_conection_server(self, mensaje):
        # CHANGE: Esta línea no es necesaria porque esos parámetros se obtienen al tirar el script
        # dirección del servidor del banco
        # server_bank_direction = ("127.0.0.0", 5555)
        # UDP socket
        with socket(AF_INET, SOCK_DGRAM) as udp_socket:
            udp_socket.sendto(mensaje.encode("utf-8"), (BANK_IP, BANK_PORT))
            # FIXME: Cambia este y TODOS los prints por mensajes usando el LOGGER
            print("Mensaje enviado al servidor del banco")

            response, _ = udp_socket.recvfrom(1024)
            # FIXME: Cambia este y TODOS los prints por mensajes usando el LOGGER
            print("Respuesta del servidor del banco:", response.decode("utf-8"))

            if response.decode("utf-8") == "OK":
                # FIXME: Cambia este y TODOS los prints por mensajes usando el LOGGER
                print(
                    "La transacción fue exitosa. Entregar el licor virtual al usuario."
                )
                # tomemos a Username como el uuid
                user_name = "NombreUsuario"  # Reemplaza con el nombre de usuario real
                liquor_name = "NombreLicor"  # Reemplaza con el nombre del licor real
                liquor_delivery = LiquorDelivery(user_name)
                liquor_delivery.deliver_liquor(liquor_name)

class Litlerhitler(BaseRequestHandler):
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


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create console handler and set the level to DEBUG
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = Formatter()

    # Add the formatter to the handler
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)

    return logger


if __name__ == "__main__":
    # Enable logger and configure it
    LOGGER = setup_logger()

    # Check correct number or arguments
    if len(argv) != 5:
        LOGGER.info(
            "Usage: server.py <liquor_store_server_IP> <liquor_store_port> <bank_IP> <bank_port>"
        )
        exit(1)

    # Extract arguments
    LIQUOR_STORE_SERVER_IP, LIQUOR_STORE_PORT, BANK_IP, BANK_PORT = argv[1:]

    # Declare global variables and initialize them
    global STORE, connected_users
    STORE = Store()
    connected_users = []

    # Create servers and their threads
    TCP_SERVER = ForkingUDPServer(
        (LIQUOR_STORE_SERVER_IP, int(LIQUOR_STORE_PORT)), Litlerhitler
    )
    # ↑↑↑ FIX ME: Cambia el BankUDPServerHandler por tu clase handler personalizada ↑↑↑
    UDP_SOCKET = socket(AF_INET, SOCK_DGRAM)

    try:
        TCP_SERVER.serve_forever
        LOGGER.info(
            f"TCP Server listening on {LIQUOR_STORE_SERVER_IP}:{LIQUOR_STORE_PORT}"
        )

    except KeyboardInterrupt:
        # Empty print to not have the ^C in the same line as the warn
        print("")
        LOGGER.warning("Stopping server, please wait...")

        # Shutdown both servers
        TCP_SERVER.shutdown()
