# -*- coding: utf-8 -*-

from odoo.upgrade import util
from odoo.upgrade.util import expand_braces as eb


def migrate(cr, version):
    util.rename_xmlid(cr, *eb("pos_epson_printer.view_{restaurant_printer_iot_form,pos_printer_form}"))
