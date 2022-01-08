""""
This is a fork of python_orm_sqlite package in order to make an abstraction of sqlite3 lib
"""


import sqlite3
import datetime
import pathlib
import os
import logging
import inspect
import sys


logger = logging.getLogger()
DBNAME = r"C:\Users\DNA\Documents\database\test0.db"


class Manager:
    def __init__(self):
        
        pass

    def get_class_fields(object):
        fname = object.table
        fields = []
        with open("objects/" + fname + ".py", "r") as ins:
            for line in ins:
                if "##" in line:
                    line = line.strip()
                    field = line.split(" ", 1)[0]
                    fields.append(field)

        return fields

    def get_current_date_as_string(self):
        """"

        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update(self, object):
        object.updated = self.get_current_date_as_string()

        result = "ok"
        query = "update " + object.table + " set "
        fields = self.get_class_fields(object)

        for x in range(0, len(fields)):
            fieldname = fields[x]

            if fieldname == "created":
                continue

            query += fieldname + " = "
            attr = getattr(object, fieldname)
            if type(attr) is str:
                query += "'"
            query += str(attr)
            if type(attr) is str:
                query += "'"

            if x != len(fields) - 1:
                query += ", "

        idfield = fields[0]
        id = getattr(object, idfield)

        query += " where " + idfield + " = '" + id + "'"

        print(query)

        conn = sqlite3.connect(DBNAME)
        c = conn.cursor()

        try:
            c.execute(query)
        except Exception as e:
            print(e)
            result = "error"
        finally:
            conn.commit()
            conn.close()

        return result

    def create(self, object):
        object.created = self.get_current_date_as_string()
        object.updated = self.get_current_date_as_string()

        result = "ok"
        query = "insert into " + object.table + " ("

        fields = self.get_class_fields(object)

        for x in range(0, len(fields)):
            fieldname = fields[x]
            query += fieldname
            if x != len(fields) - 1:
                query += ", "

        query += ") values ("

        for x in range(0, len(fields)):
            field = fields[x]
            if type(getattr(object, field)) is str:
                query += "'"
            query += str(getattr(object, field))
            if type(getattr(object, field)) is str:
                query += "'"
            if x != len(fields) - 1:
                query += ", "

        query += ")"

        print(query)

        conn = sqlite3.connect(DBNAME)
        c = conn.cursor()

        try:
            c.execute(query)
        except Exception as e:
            if 'UNIQUE constraint' in e.message:
                result = "already exists"
            else:
                print(e)
                result = "error"
        finally:
            conn.commit()
            conn.close()

        return result

    def fetch(self, object):
        fields = self.get_class_fields(object)
        idfield = fields[0]
        id = getattr(object, idfield)

        conn = sqlite3.connect(DBNAME)
        c = conn.cursor()

        c.execute("SELECT * FROM " + object.table + " WHERE " + idfield + " = '" + id + "'")
        r = c.fetchone()

        for x in range(0, len(fields)):
            name = fields[x].split(" ", 1)[0]
            value = r[x]
            setattr(object, name, value)

        conn.commit()
        conn.close()

        return object


class dbriver:
    def init(self):
        print("creating database with next structure:")
        classes = []

        print(DBNAME)

        conn = sqlite3.connect(DBNAME)
        c = conn.cursor()

        for name, obj in inspect.getmembers(sys.modules[__name__]):
            if inspect.isclass(obj):
                classes.append(obj)
                query = ""
                print("class: " + str(obj))
                print("table: " + str(obj.table))
                query += "create table if not exists " + str(obj.table) + "("

                fields = Manager.getClassFields(obj)

                for x in range(0, len(fields)):
                    field = fields[x]
                    print("         " + field)
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
                print(query)

        conn.commit()
        conn.close()

        return

    def drop(self):
        if os.path.isfile(DBNAME):
            os.remove(DBNAME)
        return

    def remake(self):
        drop()
        init()
        return

