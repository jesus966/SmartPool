import logging
import pymongo

from src.database.models import ChemicalTankData
from src.database.db import db
import datetime
import src.strings_constants.strings as strings

from pymongo import errors

class ChemicalTank:
    """
    This class represents a chemical tank of the pool
    """

    tank_type = None
    current_liters = None
    max_capacity = None
    datetime = None

    def __init__(self, tank_type, max_capacity, load=True):
        """
        Constructor of the class
        """

        self.tank_type = tank_type
        self.max_capacity = max_capacity
        self.current_liters = max_capacity
        logging.log(logging.DEBUG, strings.LOG_CHEM_INSTANTIATED, tank_type, max_capacity)
        if load:
            self.load_from_db()

    def set_value(self, value):
        """
        This method sets the amount of liters to a given value.
        """
        self.current_liters = value
        self.save_to_db()
        logging.log(logging.INFO, strings.LOG_CHEM_SET_VALUE, self.tank_type, value)

    def decrease_value(self, value):
        """
        This method decreases the amount of litres that the tank stores
        """
        self.current_liters = self.current_liters - value
        self.save_to_db()
        logging.log(logging.INFO, strings.LOG_CHEM_DEC_VALUE, self.tank_type, value, self.current_liters)

    def refill(self):
        """
        This method "refills" the current tank capacity
        """
        self.current_liters = self.max_capacity
        self.save_to_db()
        logging.log(logging.INFO, strings.LOG_CHEM_REFILLED, self.tank_type)

    def save_to_db(self):
        """
        This method saves the current data into the database
        """
        try:
            col = db.get_db().get_collection("chemical_tank_data")
            self.datetime = datetime.datetime.utcnow()
            tank_db = ChemicalTankData()
            tank_db.tank_type = self.tank_type
            tank_db.current_liters = self.current_liters
            tank_db.datetime = self.datetime
            col.replace_one({"tank_type": self.tank_type}, tank_db.to_mongo(), upsert=True)
        except errors.PyMongoError:
            pass

    def load_from_db(self):
        """
        This method search from the latest record in the database
        of this tank type and gets the last capacity.
        """

        # Search into the database for the most recent record
        try:
            col = db.get_db().get_collection("chemical_tank_data")
            record = col.find({"tank_type": self.tank_type}).limit(1).sort("datetime", pymongo.DESCENDING)[0]
            self.current_liters = record["current_liters"]
            logging.log(logging.INFO, strings.LOG_CHEM_LOADED, self.tank_type, self.current_liters)
        except IndexError:
            logging.log(logging.INFO, strings.LOG_CHEM_LOAD_FAIL, self.tank_type)
            self.current_liters = self.max_capacity

    def __eq__(self, other):
        """
        This method checks the equality of two ChemicalTank Classes
        """
        if isinstance(other, ChemicalTank):
            return self.current_liters == other.current_liters and self.max_capacity == other.max_capacity \
                   and self.tank_type == other.tank_type

        return False
