# -*- coding: utf-8 -*-


from typing import List, Tuple, Dict

from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QAction, QComboBox, QMessageBox


def info(parent, header, msg):
    """
    Displays an information window.

    :param parent:
    :param header:
    :param msg:
    :return:
    """
    
    QMessageBox.information(parent, header, msg)


def warn(parent, header, msg):
    """
    Displays a warning window.

    :param parent:
    :param header:
    :param msg:
    :return:
    """

    QMessageBox.warning(parent, header, msg)


def error(parent, header, msg):
    """
    Displays an error window.

    :param parent:
    :param header:
    :param msg:
    :return:
    """

    QMessageBox.error(parent, header, msg)
    
def make_qaction(tool_params: Dict, plugin_nm: str, icon_fldr: str, parent: 'QObject'):
    """
    Creates a QAction instance.
    Expected keys in params dictionary:
        tool_nm: the tool name, string;
        icon_nm: the name of the icon, string;
        whtsths_dscr: the action description, string.
    Used for QGIS Python plugin.

    :param tool_params: QAction text parameters.
    :type tool_params: dictionary.
    :param plugin_nm: name of the plugin.
    :type plugin_nm: str.
    :param icon_fldr: icon folder name (assume single nesting).
    :type icon_fldr: str.
    :param parent: the parent widget.
    :type parent: QObject or null pointer.
    :return:
    """

    q_icon_path = ":/plugins/{}/{}/{}".format(
            plugin_nm,
            icon_fldr,
            tool_params["icon_nm"])

    geoproc = QAction(
        QIcon(q_icon_path),
        tool_params["tool_nm"],
        parent)

    geoproc.setWhatsThis(tool_params["whtsths_dscr"])

    return geoproc


def update_combo_box(combobox: QComboBox, init_text: str, texts: List[str]):
    """
    Updates a combo box content using a list of strings.

    :param combobox: the combobox to be updated
    :param init_text: the initial updated combo box element
    :param texts: the list of the texts used to fill the combo box
    :return:
    """

    combobox.clear()

    if len(texts) == 0:
        return

    if init_text:
        combobox.addItem(init_text)

    combobox.addItems(texts)


def qcolor2rgbmpl(qcolor: QColor) -> Tuple[float, float, float]:
    """
    Calculates the red, green and blue components of the given QColor instance.

    :param qcolor: the input QColor instance
    :type qcolor: QColor
    :return: the triplet of the three RGB color values
    :type: a tuple of three floats
    """

    red = qcolor.red() / 255.0
    green = qcolor.green() / 255.0
    blue = qcolor.blue() / 255.0

    return red, green, blue

