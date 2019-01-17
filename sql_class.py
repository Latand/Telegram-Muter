#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
import sqlite3
import logging


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Mysql(object):
    def __init__(self, debug=False):
        self.connection = None  # self.connect()
        self.debug = debug
        self.if_cursor_dict = False

    def connect(self):
        self.connection = sqlite3.connect("mydb")
        return self.connection

    def insert(self, table, returning=False, **kwargs):
        what = []
        if "what" in kwargs.keys():
            if isinstance(kwargs["what"], str):
                what = [kwargs["what"]]
            else:
                what = kwargs["what"]
            iterate = ", ".join(["?" for _ in range(len(what))])
            if isinstance(kwargs["where"], list):
                where = ", ".join([
                    f"`{item}`" for item in kwargs["where"]
                ])
            else:
                where = kwargs["where"]
        else:
            where = ""
            iterate = ""
            for key, value in kwargs.items():
                if key not in ["returning", "table"]:
                    where += "{}, ".format(key)
                    iterate += "?, "
                    what.append(value)
            iterate = iterate[:-2]
            where = where[:-2]
        command = "INSERT INTO `{0}`({1}) VALUES ({2})".format(
            table, where, iterate
        )
        return self.execute(command, what, returning=returning)

    def select(self, **kwargs):
        args = []
        if "what" not in kwargs.keys():
            what = "*"
        elif any([x in kwargs["what"] for x in ["SUM", "COUNT", "DISTINCT", "MAX"]]):
            what = kwargs["what"]
        else:
            if isinstance(kwargs["what"], str):
                kwargs["what"] = [kwargs["what"]]
            what = ", ".join([f"`{column_name}`" for column_name in kwargs["what"]])
        command = "SELECT {0} FROM {1} ".format(
            what, kwargs["where"]
        )
        if "condition" in kwargs:
            command += " WHERE "
            for item, value in kwargs["condition"].items():
                if not any([x in str(value) for x in ["<", ">", "!", "IS"]]):
                    if isinstance(value, str):
                        command += " `{}` = ? AND".format(item)
                        args.append(value)
                    else:
                        command += " `{}` = ? AND".format(item)
                        args.append(value)
                else:
                    command += " `{}` {} AND".format(item, value)
            command = command[:-3] if command.endswith("AND") else command
        if "order" in kwargs:
            command += " ORDER BY {}".format(kwargs["order"])

        if "limit" in kwargs:
            command += " LIMIT {}".format(kwargs["limit"])
        return self.execute(command, args, select=True, kwargs=kwargs)

    def delete(self, table, where, what):
        if where is None:
            return self.execute(command="DELETE FROM {} WHERE 1".format(table))
        if isinstance(where, str):
            where = [where]
        where = "AND ".join(["`{}` = ? ".format(wher) for wher in where])
        return self.execute(command="DELETE FROM `{}` WHERE {}".format(table, where),
                            args=what)

    def update(self, table, **kwargs):
        args = []
        command = "UPDATE `{0}` SET ".format(table)
        for items, value in kwargs.items():
            if items != "condition":
                if items == "raw":
                    continue
                if "CURRENT_TIMESTAMP" not in str(value):
                    command += " `{}` = ?,".format(items) if "raw" not in kwargs else " `{}` = {},".format(items,
                                                                                                           value)
                    args.append(value)

                else:
                    command += f" `{items}` = {value},"
        command = command[:-1] if command.endswith(",") else command
        command += " WHERE "
        if "condition" in kwargs:
            for item, value in kwargs["condition"].items():
                command += " `{}` = ? AND".format(item) if "raw" not in kwargs else " `{}` = {} AND".format(item,
                                                                                                            value)
                args.append(value)
        command = command[:-3] if command.endswith("AND") else command
        if "raw" in kwargs:
            args.clear()
        self.execute(command, args, kwargs=kwargs)

    def execute(self, command, args=(), select=False, returning=False, kwargs={}):
        self.connection = self.connect()
        c = None

        self.connection.row_factory = dict_factory
        if self.debug:
            with self.connection.cursor(c) as cursor:
                print(command, args, kwargs)
                cursor.execute(command, (*args,))
                if returning:
                    ids = cursor.lastrowid
                self.connection.commit()
            if select:
                values = cursor.fetchall()
                self.connection.close()
                if len(values) == 1:
                    if isinstance(values[0], tuple) and len(values[0]) == 1:
                        values = values[0][0]
                print(str(values).encode())
                return values
            elif returning:
                return ids
        else:
            cursor = self.connection.cursor()
            try:
                cursor.execute(command, (*args,))
                if returning:
                    ids = cursor.lastrowid
            except sqlite3.OperationalError as err:
                print("Operational error. restart {}\n{}\n{}".format(command, kwargs, err))
                self.connection.close()
                return

            except sqlite3.InterfaceError as err:
                print("InterfaceError (bad command), "
                      "reconnecting, executing", err)
                logging.info("InterfaceError (bad command), "
                             "reconnecting, executing, {}".format(err))

                self.connection.close()
                return

            except sqlite3.ProgrammingError as err:
                print("Programming error (bad command), {} \n{} ".format(err, [command, kwargs, args]))
                logging.info("Programming error (bad command), {} \n{} ".format(err, [command, kwargs, args]))
                return

            except sqlite3.IntegrityError as err:
                logging.info(f"IntegrityError, dublicate primary key? {err}")
                print("IntegrityError, dublicate primary key? ", err)
                return

            except Exception as err:
                print("Other error. {}\n {}, \n{}".format(command, kwargs, err))
                logging.info("Other error. {}\n {}, \n{}".format(command, kwargs, err))
                return

            if select:
                values = cursor.fetchall()
                self.connection.close()
                if len(values) == 1:
                    if isinstance(values[0], tuple) and len(values[0]) == 1:
                        values = values[0][0]

                return values
            else:
                self.connection.commit()
                self.connection.close()
                if returning:
                    return ids


sql = Mysql()
