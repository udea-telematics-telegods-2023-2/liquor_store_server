from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from src.db import Liquor, LiquorDatabase
from uuid import uuid4
import json

class Store:
    def __init__(self, database: LiquorDatabase = LiquorDatabase()):
        self.__database = database
    def check_liquor(self, uuid: str = "") -> tuple[int,str]:
        if uuid == "": #si dejan el espacio de nombre vacio
            return 253, ""
        free_liquor_name = self.__database.read(uuid=uuid) 
        if not free_liquor_name:  #si no se encuentra el licor en la tienda      
            return 252, ""
        liquor_data = free_liquor_name.get_data()
        if liquor_data[3] == 0: #si no hay stock del licor pedido
            return 253
        if free_liquor_name:
            return 0, "ok"
    def list(self) -> tuple[int,str]: 
        free_liquors_name = self.__database.read_all() 
        list_liquors_name = json.dumps(list_liquors_name)

        #restored_list_liquors = json.loads(list_liquors_name)

        return 0, list_liquors_name





