from src.db import Liquor, LiquorDatabase
import json


class LiquorStore:
    def __init__(self, database: LiquorDatabase = LiquorDatabase()):
        self.__database = database

    def check_liquor(self, uuid: str = "") -> tuple[int, str]:
        if uuid == "":
            return 253, ""

        liquor = self.__database.read(uuid=uuid, read_all=False)
        if isinstance(liquor, Liquor):
            liquor_data = liquor.get_data()
            if liquor_data[3] == 0:
                return 4, ""
            return 0, ""
        return 252, ""

    def substract_stock(self, uuid: str = "") -> tuple[int, str]:
        if uuid == "":
            return 253, ""

        self.__database.update(uuid=uuid, delta_stock=-1)
        return 0, ""

    def list(self) -> tuple[int, str]:
        liquors = self.__database.read(read_all=True)
        liquors_list = []
        if isinstance(liquors, list):
            liquors_list = [liquor.get_data() for liquor in liquors]
        return 0, json.dumps(liquors_list)

    def get_liquor_name(self, uuid: str = "") -> tuple[int, str]:
        if uuid == "":
            return 253, ""

        liquor = self.__database.read(uuid=uuid, read_all=False)
        if isinstance(liquor, Liquor):
            liquor_name = liquor.get_data()[1]
            return 0, liquor_name
        return 252, ""

    def get_liquor_price(self, uuid: str = "") -> tuple[int, str]:
        if uuid == "":
            return 253, ""

        liquor = self.__database.read(uuid=uuid, read_all=False)
        if isinstance(liquor, Liquor):
            liquor_price = liquor.get_data()[4]
            return 0, str(liquor_price)
        return 252, ""
