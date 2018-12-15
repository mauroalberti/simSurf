# -*- coding: utf-8 -*-


from typing import List, Tuple, Dict, Optional, Union

from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtSql import QSqlDatabase, QSqlQuery


def try_connect_to_sqlite3_db_with_qt(db_path: str, conn_type: str= "readwrite") -> Tuple[bool, str]:
    """
    Open ans sqlite3 database for reading/writing, based on connection option.

    :param db_path: the path to the database.
    :type db_path: str.
    :param conn_type: the connection type, i.e. for reading/writing.
    :type conn_type: str.
    :return: the success status and a message.
    :rtype: a tuple made up by a boolean and a string.
    """

    try:

        if conn_type == "readonly":
            conn_opt_str = "QSQLITE_OPEN_READONLY;"
        elif conn_type == "readwrite":
            conn_opt_str = "SQLITE_OPEN_READWRITE;"
        else:
            raise Exception("Unimplemented connection option: {}".format(conn_type))

        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setConnectOptions(conn_opt_str)
        db.setDatabaseName(db_path)
        success = db.open()

        if success:
            return True, ""
        else:
            return False, "Unable to connect to {} with error {}".format(
                db_path,
                db.lastError().text())

    except Exception as e:

        return False, "Exception: {}".format(e)


def get_selected_recs_ids(selection_model: QItemSelectionModel, ndx_col: int=0) -> Optional[Tuple[int, ...]]:
    """
    Get integer ids from selected records.
    Unless explicitely defines, it assumes that id is stored in column 0.

    :param selection_model: the selection model.
    :type selection_model: QItemSelectionModel.
    :param ndx_col: the index of the searched columns.
    :type ndx_col: int.
    :return: the sequence of ids.
    :rtype: tuple of integers.
    """

    # get selected records attitudes

    selected_records_ids = selection_model.selectedRows(column=ndx_col)

    if selected_records_ids:
        return tuple(map(lambda qmodel_ndx: qmodel_ndx.data(), selected_records_ids))
    else:
        return None


def try_execute_query_with_qt(query: str) -> Tuple[bool, Union[str, QSqlQuery]]:
    """
    Executes a query in a database using qt tools.

    :param query: the query to be executed.
    :type query: string.
    :return: the success status and the query results.
    :rtype: a tuple of a boolean and a string or a QSqlQuery instance.
    """

    sqlquery = QSqlQuery(QSqlDatabase.database())
    success = sqlquery.exec(query)

    if success:
        return True, sqlquery
    else:
        return False, "Error with query {}".format(query)


