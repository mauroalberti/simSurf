
from typing import List, Tuple, Dict, Union

import sqlite3


def try_create_table(cursor: sqlite3.Cursor, table_name: str, fields_pars: List[Dict[str, Dict[str, str]]]) -> Tuple[bool, str]:
    """
    Try creating a table, dropping the previous one if existing.

    :param cursor: the sqlite3 databasse cursor.
    :type cursor: sqlite3.Cursor.
    :param table_name: the name of the table to be created.
    :type table_name: str.
    :param fields_pars: fields parameters, provided as a list of field dictionaries.
                Each field dictionary has its applicative name as key and
                as value a dictionary with a pair of keys-values:
                    "name": name of the field, as a string.
                    "type": field type, as a string.
    :type fields_pars: List[Dict[(str, str)]].
    :return: success and message
    :rtype: tuple of boolean and string.

    """

    try:
        cursor.execute('''DROP TABLE IF EXISTS {table_name}'''.format(table_name=table_name))

        flds_parts = []
        for dct in fields_pars:
            fld_ident = list(dct.keys())[0]
            flds_parts.append("{} {}".format(dct[fld_ident]["name"], dct[fld_ident]["type"]))

        flds_string = ", ".join(flds_parts)
        query_string = '''CREATE TABLE {table_name} ({flds})'''.format(
            table_name=table_name,
            flds=flds_string)

        cursor.execute(query_string)

        return True, "Completed"

    except Exception as e:

        return False, "Exception: {}".format(e)


def try_create_db_tables(db_path: str, tables_pars: List[Dict[str, Union[str, List[Dict[str, Dict[str, str]]]]]]) -> Tuple[bool, str]:
    """
    Try creating (if not existing) and populating a database
    with tables.

    :param db_path: the path of the database.
    :type db_path: str.
    :param tables_pars: the parameters of the tables to be created
    :type tables_pars: list.
    :return: success and message
    :rtype: tuple of boolean and string.

    """

    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        return False, "Unable to create database {} (Exception message: {}).\nPossibly folder permission error?".format(
            db_path,
            e)

    try:

        curs = conn.cursor()

        for table_pars in tables_pars:
            table_name = table_pars["name"]
            table_fields_params = table_pars["fields"]

            success, msg = try_create_table(
                cursor=curs,
                table_name=table_name,
                fields_pars=table_fields_params)
            if not success:
                return False, "Unable to create table {} with Exception: {}".format(table_name, msg)

        conn.commit()
        conn.close()

        return True, "Completed"

    except Exception as e:

        return False, "Exception: {}"


def try_execute_query_with_sqlite3(db_path: str, query: str) -> Tuple:
    """
    Execute a query in sqlite3 and return the results as a tuple.

    :param db_path: path of database.
    :type db_path: str.
    :param query: the query to be executed.
    :type query: str.
    :return: the results as a tuple.
    :rtype: Ttple.
    """

    try:

        conn = sqlite3.connect(db_path)
        curs = conn.cursor()
        curs.execute(query)
        results = curs.fetchall()
        conn.close()

        return True, results

    except Exception as e:

        return False, "Exception: {}".format(e)


