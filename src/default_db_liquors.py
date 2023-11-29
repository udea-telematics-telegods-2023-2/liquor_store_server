#!/usr/bin/python

import uuid
from src import db

# Static user data
commercial_names = ["Vodka", "Soju", "Sake", "Aguardiente", "Beer"]
country_codes = ["ru", "kr", "jp", "co", "de"]
stocks = [6, 5, 7, 3, 10]
prices = [114_900, 98_900, 325_800, 40_700, 3_500]

# UUID for each user, username, hashed password and initial balance
liquors = [
    db.Liquor(str(uuid.uuid4()), commercial_name, country_code, stock, price)
    for commercial_name, country_code, stock, price in zip(
        commercial_names, country_codes, stocks, prices
    )
]

# Create new database
database = db.LiquorDatabase()

# Insert default clients
for liquor in liquors:
    database.create(liquor)
