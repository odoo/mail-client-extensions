# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_module(cr, "pos_reprint")

    if util.has_enterprise():
        util.merge_module(cr, "iot_pairing", "iot")
