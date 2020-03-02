# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "confirm.stock.sms", "picking_id")
    util.remove_field(cr, "confirm.stock.sms", "company_id")
