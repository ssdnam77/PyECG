""""

"""

import sqlite3
import pathlib
import logging
import os

logger = logging.getLogger()


class dbdrv:
    def __init__(self, conector=None, cursor=None):
        self.cursor = cursor
        self.conn = conector
        pass

    def connect_db(self, path=None):
        wpath = pathlib.Path(path)
        if wpath.exists():
            try:
                conn = sqlite3.connect(wpath)
                # self.cursor = conn.cursor()
                # consulta = 'CREATE TABLE Persona (CI varchar(11) NOT NULL, Nombre varchar(255), Apellido1 varchar(255));'
                # self.cursor.execute(consulta)
                # conn.commit()
                # self.cursor.execute("CREATE UNIQUE INDEX Persona_CI ON Persona (CI);")
                # conn.commit()
                # conn.close()
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                logger.debug(message)

    # def

def main(pt):
    db = dbdrv()
    db.connect_db(pt)


if __name__ == '__main__':
    loc = pathlib.PurePath(r"C:\Users\DNA\Documents\database\test1.db")
    main(loc)
