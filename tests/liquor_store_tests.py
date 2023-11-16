import unittest
from src.db.db import Liquor, LiquorDatabase


class TestLiquorStoreDB(unittest.TestCase):
    def setUp(self):
        # Initialize a LiquorDatabase instance
        self.liquor_db = LiquorDatabase()

    def test_liquor_creation_and_retrieval(self):
        # Create a liquor
        liquor1 = Liquor("aaaa-aaaa-aaaa-aaaa", "test_liquor1", "co", 5, 1000)

        # Add the liquor to the database
        self.liquor_db.create(liquor1)

        # Retrieve the liquor from the database
        retrieved_liquor = self.liquor_db.read(liquor1.get_data()[0])

        self.assertIsNotNone(retrieved_liquor)

        # Assert that the retrieved liquor matches the original liquor
        if retrieved_liquor is not None:
            self.assertEqual(liquor1.get_data(), retrieved_liquor.get_data())

    def test_stock_update(self):
        initial_stock = 5
        liquor2 = Liquor(
            "bbbb-bbbb-bbbb-bbbb", "test_liquor2", "us", initial_stock, 1000
        )
        self.liquor_db.create(liquor2)

        # Update the liquor's stock
        delta_stock = 3
        self.liquor_db.update(liquor2.get_data()[0], delta_stock=delta_stock)

        # Retrieve the updated liquor from the database
        expected_stock = initial_stock + delta_stock
        updated_liquor = self.liquor_db.read(liquor2.get_data()[0])

        if updated_liquor is not None:
            self.assertEqual(expected_stock, self.liquor_db.read(liquor2)[3])

    def test_price_update(self):
        initial_price = 5000.0
        liquor3 = Liquor("cccc-cccc-cccc-cccc", "test_liquor3", "de", 5, initial_price)
        self.liquor_db.create(liquor3)

        # Update the liquor's price
        new_price = 7000.0
        self.liquor_db.update(liquor3.get_data()[0], new_price=new_price)

        # Retrieve the updated liquor from the database
        updated_liquor = self.liquor_db.read(liquor3.get_data()[0])

        if updated_liquor is not None:
            self.assertEqual(updated_liquor.get_data()[4], new_price)

    def tearDown(self):
        # Clean up the database after tests
        self.liquor_db.delete("aaaa-aaaa-aaaa-aaaa")
        self.liquor_db.delete("bbbb-bbbb-bbbb-bbbb")
        self.liquor_db.delete("cccc-cccc-cccc-cccc")
        pass


if __name__ == "__main__":
    unittest.main()
