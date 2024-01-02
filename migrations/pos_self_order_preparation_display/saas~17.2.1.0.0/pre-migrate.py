# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "pos_preparation_display.order", "pos_take_away", "pos_takeaway")
