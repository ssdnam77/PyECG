import sqlite3, sys, inspect, os, logging
from utils import manager
from utils.objects.paciente import Paciente
from utils.objects.registro import Registro
# any new entity in the db it must import here in order to init the schema of the new db
logger = logging.getLogger()


def init():
    logger.info("creating database with next structure:")
    classes = []

    logger.info(manager.DBNAME) # use to by a print() insted a logger() here

    conn = sqlite3.connect(manager.DBNAME)
    c = conn.cursor()

    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            classes.append(obj)
            query = ""
            logger.info("class: " + str(obj))
            logger.info("table: " + str(obj.table))
            query += "create table if not exists " + str(obj.table) + "("

            fields = manager.getClassFields(obj)

            for x in range(0, len(fields)):
                field = fields[x]
                logger.info( "         " + field)
                query += field + " "
                f = getattr(obj, field)

                if type(f) is str:
                    query += "VARCHAR"
                elif type(f) is int:
                    query += "INTEGER"

                if x == 0:
                    query += " PRIMARY KEY"

                if x != len(fields) - 1:
                    query += ", "

            query += ")"

            c.execute(query)
            logger.info(query)

    conn.commit()
    conn.close()

    return

def drop():
    if os.path.isfile(manager.DBNAME):
        os.remove(manager.DBNAME)
    return


def remake():
    drop()
    init()
    return
