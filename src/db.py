import sqlite3
from dataclasses import dataclass

# Import utils
from src.utils import get_project_root

PROJECT_ROOT = get_project_root()  # obtener la raíz de la carpeta


@dataclass
class Liquor:
    """
    Represents the information recorded in the liquor store
    with a unique liquor alidentifier (UUID),
    a commercial name, a country code for each liquor,
    the stock for each product, and the price.

    Attributes:
        uuid (str): A unique identifier (UUID) for the liquor.
        commercial_name (str): The commercial name associated with the liquor.
        country_code (str): The country code of the liquor.
        stock (int): The amount of liquor in the store.
        price (float): The price associated for each liquor.


    Methods:
        get_data() -> tuple[str, str, str, int, float]:
            Retrieves the liquor data as a tuple containing UUID,
            liquor name, country code, existing stock, and price.
    """

    uuid: str
    commercial_name: str
    country_code: str
    stock: int
    price: float = 0.0

    def get_data(self) -> tuple[str, str, str, int, float]:
        """
        Retrieves the liquor data as a tuple containing UUID,
            liquor name, country code, existing stock, and price.
        Returns:
            tuple[str, str, str, int, float]: A tuple containing Liquor data.
        """
        return (
            self.uuid,
            self.commercial_name,
            self.country_code,
            self.stock,
            self.price,
        )


class LiquorDatabase:
    """
    A class representing a liquor database with methods to interact with liquor data.

    Attributes:
        db_path (str): The path to the SQLite database file.

    Methods:
        create(liquor: Liquor): Inserts a new liquor into the database.
        read(uuid: str): Reads an existing liquor from the database.
        update(uuid: str, country_code: str, price: float): Updates a country_code or adds to the price of an existing liquor.
        delete(uuid: str): Removes an existing liquor from the database.

    Note:
        This class assumes the existence of a 'liquor_store' table in the database with columns
        'uuid', 'liquor_name', 'country_code', 'stock', and 'price'.
    """

    def __init__(self, db_path: str = f"{PROJECT_ROOT}/db/liquor_store.db"):
        """
        Initializes the database with a standard liquor_store table containing the
        Liquor data.

        Args:
            db_path (str): The path to the DB, defaults to {PROJECT_ROOT}/db/liquor.db
        """
        self.__db_path: str = db_path
        with sqlite3.connect(self.__db_path) as connection:
            connection.execute(
                """
                    CREATE TABLE IF NOT EXISTS liquor_store (
                        uuid TEXT PRIMARY KEY,
                        commercial_name TEXT UNIQUE,
                        country_code TEXT,
                        stock INTEGER,
                        price REAL
                    );
                    """
            )

    def create(self, liquor: Liquor):
        """
        Inserts a new liquor into the 'liquor_store' table of the database.

        Args:
            liquor (Liquor): The Liquor instance to be inserted into the database.
        """
        with sqlite3.connect(self.__db_path) as connection:
            connection.execute(
                """
                    INSERT INTO liquor_store (uuid, commercial_name, country_code, stock, price)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(commercial_name) DO NOTHING;
                """,
                liquor.get_data(),
            )

    def read(
        self, uuid: str = "", read_all: bool = False
    ) -> Liquor | list[Liquor] | None:
        """
        Retrieves a UUID from the 'liquor_store' table.

        Args:
            uuid (str): The UUID of the liquor to be retrieved.

        Returns:
            Liquor | None: A Liquor instance if found, or None if the liquor is not found.
        """
        with sqlite3.connect(self.__db_path) as connection:
            cursor = connection.cursor()
            if not read_all:
                result = cursor.execute(
                    """
                        SELECT * FROM liquor_store WHERE uuid = ?
                    """,
                    (uuid,),
                )
                liquor = result.fetchone()
                return Liquor(*liquor) if liquor is not None else liquor

            result = cursor.execute(
                """
                    SELECT * FROM liquor_store
                """
            )
            liquors = result.fetchall()
            return [Liquor(*liquor) for liquor in liquors] if liquors != [] else liquors

    def update(self, uuid: str, delta_stock: int = 0, price: float = -1):
        """
        Updates liquor information in the 'liquor_store' table.

        Args:
            uuid (str): The UUID of the liquor to be updated.
            delta_stock (int, optional): The new stock for the liquor. tells the total stock of a specific liquor.
            price (float, optional): The change in price for the liquor. Defaults to -1.

        Raises:
            NameError: If the liquor with the specified UUID is not found.

        Note:
            If both 'delta_stock' and 'price' are provided, the function updates both.
        """

        def __update_stock(uuid: str, delta_stock: int):
            """
            Updates the stock for a liquor in the 'liquor_store' table.

            Args:
                uuid (str): The UUID of the liquor.
                delta_stock (int): The change in stock for the liquor.
            """
            with sqlite3.connect(self.__db_path) as connection:
                liquor = self.read(uuid)
                if liquor is None:
                    raise NameError(f"Liquor with UUID {uuid} not found.")
                if not isinstance(liquor, Liquor):
                    return
                current_stock = liquor.get_data()[3]
                new_stock = current_stock + delta_stock
                if new_stock < 0:
                    raise ValueError("Insufficient stock.")
                else:
                    connection.execute(
                        """
                            UPDATE liquor_store
                            SET stock = ?
                            WHERE uuid = ?
                        """,
                        (new_stock, uuid),
                    )

        def __update_price(uuid: str, price: float):
            """
            Updates the price for a liquor in the 'liquor_store' table.

            Args:
                uuid (str): The UUID of the liquor.
                price (float): The change in price for the liquor.
            """
            with sqlite3.connect(self.__db_path) as connection:
                connection.execute(
                    """
                        UPDATE liquor_store
                        SET price = ?
                        WHERE uuid = ?
                    """,
                    (price, uuid),
                )

        if delta_stock != 0:
            __update_stock(uuid, delta_stock)

        if price >= 0.0:
            __update_price(uuid, price)

    def delete(self, uuid: str):
        with sqlite3.connect(self.__db_path) as connection:
            connection.execute(
                """
                    DELETE FROM liquor_store 
                    WHERE uuid = ?;
                """,
                (uuid,),
            )
