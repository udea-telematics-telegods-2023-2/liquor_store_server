from src.db import LiquorDatabase
import json


class Store:
    # FIX ME: falta documentación estilo Google de la clase, y de cada uno de sus funciones
    def __init__(self, database: LiquorDatabase = LiquorDatabase()):
        self.__database = database

    def check_liquor(self, uuid: str = "") -> tuple[int, str]:
        if uuid == "":  # si dejan el espacio de nombre vacio
            return 253, ""
        # CHANGE: cambié el nombre de free_liquor_name a liquor para
        # hacer referencia a un licor de la base de datos
        liquor = self.__database.read(uuid=uuid)
        # CHANGE: cambié la comparación para que sea explícita
        # (comparar si es del tipo None)
        # si no se encuentra el licor en la tienda
        if liquor is None:
            return 252, ""
        liquor_data = liquor.get_data()
        # si no hay stock del licor pedido
        if liquor_data[3] == 0:
            return 253, ""  # FIX ME: 253 NO ES ERROR DE STOCK
        # si todo sale bien, retornar error 0
        return 0, ""

    def list(self) -> tuple[int, str]:
        liquors = self.__database.read_all()
        list_liquors_name = json.dumps(liquors)
        # FIX ME: Borrar este comentario y todos los que puse que son reseñas
        # restored_list_liquors = json.loads(list_liquors_name)
        return 0, list_liquors_name
