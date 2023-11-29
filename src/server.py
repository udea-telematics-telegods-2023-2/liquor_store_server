#!/usr/bin/env python
from json import loads, dumps
from socket import AF_INET, SOCK_DGRAM, socket
from socketserver import ThreadingTCPServer, BaseRequestHandler
from src.liquor import LiquorStore
from src.utils import setup_logger
from sys import argv, exit

connected_users = []


class Command:
    """
    Represents a command for the liquor store with associated functions.

    Attributes:
        __command (str): The command string.
        __arguments (list): The list of arguments for the command.
        __fn (callable): The function associated with the command.
        __error_code (int): The error code resulting from the command execution.

    Methods:
        debug(): Logs a debug message when the command is executed.
        no_fn(_: None) -> tuple[int, str]: Default function for commands without an associated function.
        wrong_args(_: None) -> tuple[int, str]: Function for commands with incorrect arguments.
        __check_args(args_number: int = 0, fn: callable = no_fn): Checks and sets the associated function based on the command.
        fn() -> tuple[int, str]: Executes the associated function and returns the result.
    """

    def debug(self):
        """
        Outputs additional information to the logger.
        """
        if self.fn != self.no_fn:
            LOGGER.debug(
                f"{self.__command}:{self.__arguments} executed",
            )

    def no_fn(self, _=None) -> tuple[int, str]:
        """
        Default function for non-valid commands.
        """
        return 254, ""

    def wrong_args(self, _=None) -> tuple[int, str]:
        """
        Default function for wrong_number of arguments.
        """
        return 253, ""

    def hi(self, _=None) -> tuple[int, str]:
        """
        Function that handles first connection.
        """
        return 0, "liquor_store"

    def __check_args(self, args_number: int = 0, fn=no_fn):
        """
        Checks if the number of arguments supplied is correct.
        """
        if len(self.__arguments) != args_number:
            self.__arguments = []
            self.__fn = self.wrong_args
        else:
            self.__fn = fn

    def __init__(self, command: str, arguments: list):
        self.__command = command
        self.__arguments = arguments
        self.__fn = self.no_fn

        match self.__command:
            case "HI":
                self.__check_args(args_number=0, fn=self.hi)

            case "LIST":
                self.__check_args(args_number=0, fn=STORE.list)

            case "BUY":
                self.__check_args(args_number=1, fn=STORE.check_liquor)

            case _:
                self.__arguments = []

    def fn(self) -> tuple[int, str]:
        """
        Executes the binded function of the command and returns the error code.
        """
        self.__error_code, data = self.__fn(*self.__arguments)
        if self.__error_code == 0:
            return 0, data
        return self.__error_code, ""


class LiquorStoreTCPServerHandler(BaseRequestHandler):
    def handle_error(self, error_code: int):
        error_msg = f"Error {error_code}: "
        match error_code:
            case 1:
                error_msg += "Invalid login"
            case 2:
                error_msg += "Invalid registration"
            case 3:
                error_msg += "Insufficient funds"
            case 4:
                error_msg += "Insufficient liquor"
            case 251:
                error_msg += "Unauthorized access"
            case 252:
                error_msg += "UUID not found"
            case 253:
                error_msg += "Bad arguments"
            case 254:
                error_msg += "Unknown command"
            case 255:
                error_msg += "Unknown error"

        LOGGER.error(error_msg)

    def send_error_code(self, error_code=255):
        self.request.sendall(f"ERR {error_code}\r\n".encode("utf-8"))

    def send_ok_data(self, ok_data=""):
        self.request.sendall(f"OK {ok_data}\r\n".encode("utf-8"))

    def encrypt(self, msg: str, n: int):
        result = ""
        for char in msg:
            if char.isalpha():
                # Shift letters
                if char.islower():
                    result += chr((ord(char) - ord("a") + n) % 26 + ord("a"))
                else:
                    result += chr((ord(char) - ord("A") + n) % 26 + ord("A"))
            elif char.isdigit():
                # Shift numbers
                result += chr((ord(char) - ord("0") + n) % 10 + ord("0"))
            else:
                # Keep spaces unchanged
                result += char
        return result

    def decrypt(self, msg: str, n: int) -> str:
        return self.encrypt(msg, -n)

    def send_encrypted_data(self, conn, to, n: int, encrypted_msg: str):
        conn.sendto(self.encrypt(f"{encrypted_msg} {n}\r\n", n).encode("utf-8"), to)

    def handle(self):
        LOGGER.info(f"Accepted connection from {self.client_address}")
        connected_users.append(self.client_address)

        while True:
            # Extracts command and data from input
            data = self.request.recv(4096).decode("utf-8")

            # Check if client disconnected
            if not data:
                LOGGER.info(f"Finished connection from {self.client_address}")
                connected_users.remove(self.client_address)
                break

            # Checks non-empty message
            if len(data) <= 2:
                LOGGER.warning("Empty message")
                continue

            command, *arguments = data.split()
            cmd = Command(command, arguments)
            cmd.debug()
            LOGGER.info(f"Command {command} issued by {self.client_address}")

            error_code, cmd_return = cmd.fn()

            if error_code != 0:
                self.handle_error(error_code)
                self.send_error_code(error_code)
                continue

            if command == "LIST":
                # Talk to client
                parsed_json = loads(cmd_return)
                # Add connected users
                parsed_json.append(len(connected_users))
                # Add owner's bank account's UUID
                parsed_json.append(OWNER_UUID)
                self.send_ok_data(dumps(parsed_json))

            elif command == "BUY":
                uuid = arguments[0]
                error_code, price = STORE.get_liquor_price(uuid)
                self.send_ok_data(f"{cmd_return}{price}")

                # Extracts command and data from input
                data = self.request.recv(4096)

                # Forwards message to bank (encrypted)
                UDP_SOCKET.sendto(data, (BANK_IP, int(BANK_PORT)))

                data, _ = UDP_SOCKET.recvfrom(4096)

                # Decode the data and decrypt it
                decoded_data = data.decode("utf-8")
                LOGGER.debug(f"Encrypted message: {decoded_data}")

                if len(decoded_data) <= 1:
                    LOGGER.warning("Empty message")
                    self.finish()
                    return

                n = decoded_data.split()[-1]

                # Handle bad cypher decode number
                if not n.isdigit():
                    LOGGER.warning("Bad cypher")
                    self.finish()
                    return

                # Decrypt using the decode number
                decrypted_data = self.decrypt(decoded_data, int(n))
                processed_data = " ".join(decrypted_data.split()[:-1])
                LOGGER.debug(f"Decrypted message: {processed_data}")

                # Tell the user the response
                self.request.sendall(f"{processed_data}\r\n".encode("utf-8"))

                if processed_data.startswith("OK"):
                    error_code, liquor_name = STORE.get_liquor_name(uuid)
                    self.request.sendall(
                        f"Here, enjoy your {liquor_name}\r\n".encode("utf-8")
                    )
                    # Decrement stock
                    STORE.substract_stock(uuid)

                # Answer to client

        # connected_users.remove(self.client_address)
        self.finish()


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
    global STORE, OWNER_UUID
    STORE = LiquorStore()
    OWNER_UUID = "4e0d3bbc-fac8-4a28-909a-752f65cf9c6c"

    # Create servers
    TCP_SERVER = ThreadingTCPServer(
        (LIQUOR_STORE_SERVER_IP, int(LIQUOR_STORE_PORT)), LiquorStoreTCPServerHandler
    )
    UDP_SOCKET = socket(AF_INET, SOCK_DGRAM)

    try:
        LOGGER.info(
            f"TCP Server listening on {LIQUOR_STORE_SERVER_IP}:{LIQUOR_STORE_PORT}"
        )
        TCP_SERVER.serve_forever()

    except KeyboardInterrupt:
        # Empty print to not have the ^C in the same line as the warn
        print("")
        LOGGER.warning("Stopping server, please wait...")

        # Shutdown server
        TCP_SERVER.shutdown()
