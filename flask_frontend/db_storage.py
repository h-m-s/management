#!/usr/bin/python3
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.dialects import postgresql
from postgres_db.models.base import Base
import configparser

class PostgresStorage:
    def __init__(self):
        settings = self.parse_db_config()
        uname = settings['username']
        upass = settings['password']
        host = settings['address']
        dbname = settings['db_name']
        self.__engine = create_engine('postgresql://{}:{}@{}/{}'.format(uname, upass, host, dbname))

    def new(self, obj):
        self.session.add(obj)

    def save(self):
        self.session.commit()

    def reload(self):
        Base.metadata.create_all(self.__engine)
        self.session = scoped_session(sessionmaker(bind=self.__engine,
                                                     expire_on_commit=False))
    def parse_db_config(self):
        """
        Parses the local config file for server settings and returns
        a dictionary.
        """
        settings = {}
        config = configparser.ConfigParser()
        config.read('result_parser.cfg')
        settings['address'] = config.get('Database', 'db_address')
        settings['port'] = config.getint('Database', 'db_port')
        settings['db_name'] = config.get('Database', 'db_name')
        settings['username'] = config.get('Database', 'db_username')
        settings['password'] = config.get('Database', 'db_password')

        return settings


