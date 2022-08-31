import unittest
from src.tests.BaseCase import BaseCase
from src.models.chemicaltank import ChemicalTank
from src.database.db import db

class TankTest(BaseCase):
    def test_tank(self):
        # Create 3 tranks
        tank1 = ChemicalTank("bleach", 25)
        tank2 = ChemicalTank("bleach", 25)
        tank3 = ChemicalTank("bleach", 25)
        # Insert one value in the database
        tank1.decrease_value(1)
        # Insert another (most recent) in db
        tank2.decrease_value(2)
        # Load the most recent record from database
        tank3.load_from_db()
        # Test is OK if tank3 = tank2
        self.assertEqual(tank3.current_litters, tank2.current_litters)




if __name__ == '__main__':
    unittest.main()
