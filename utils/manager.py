import sqlite3, datetime, os, sys, pathlib

DBNAME = r"C:\Users\DNA\Documents\database\test0.db"


def getCurrentDateAsString():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def getClassFields(object):
    fname = object.table
    fields = []
    try:

        with open("../utils/objects/" + fname + ".py", "r") as ins:
            for line in ins:
                if "##" in line:
                    line = line.strip()
                    field = line.split(" ", 1)[0]
                    fields.append(field)
    except Exception as ex:
        # todo: cual es la expt
        # traceback.format_exc()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
    return fields


def update(object):
    object.updated = getCurrentDateAsString()

    result = "ok"
    query = "update " + object.table + " set "
    fields = getClassFields(object)

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


def create(object):
    object.created = getCurrentDateAsString()
    object.updated = getCurrentDateAsString()

    result = "ok"
    query = "insert into " + object.table + " ("

    fields = getClassFields(object)

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


def fetch(object):
    fields = getClassFields(object)
    idfield = fields[0]
    id = getattr(object, idfield)

    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    c.execute("SELECT * FROM " + object.table + " WHERE " + idfield + " = '" + id + "'")
    r = c.fetchone()
    if r is not None:
        fl = True
        for x in range(0, len(fields)):
            name = fields[x].split(" ", 1)[0]
            value = r[x]
            setattr(object, name, value)
    else:
        fl = False

    conn.commit()
    conn.close()

    return object, fl


def find(object):
    fields = getClassFields(object)
    idfield = fields[0]
    id = getattr(object, idfield)

    try:
        conn = sqlite3.connect(DBNAME)
    except Exception as ex:
        pass
    finally:
        c = conn.cursor()

    c.execute("SELECT * FROM " + object.table + " WHERE " + idfield + " = '" + id + "'")
    r = c.fetchone()
    if r is not None:
        fl = True
    else:
        fl = False

    conn.commit()
    conn.close()

    return fl


def delete(object):
    # todo implement delete metod

    pass
