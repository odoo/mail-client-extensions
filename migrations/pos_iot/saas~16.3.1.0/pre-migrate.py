# -*- coding: utf-8 -*-

from odoo.upgrade import util
from odoo.upgrade.util import expand_braces as eb


def migrate(cr, version):
    util.rename_xmlid(cr, *eb("pos_iot.view_{restaurant,pos}_printer_iot_form"))
    util.rename_xmlid(cr, *eb("pos_iot.view_{restaurant,pos}_printer_iot_tree"))
