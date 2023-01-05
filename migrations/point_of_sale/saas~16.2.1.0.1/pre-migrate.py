# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "point_of_sale.pos_daily_report")
    util.create_m2m(cr, "pos_config_trust_relation", "pos_config", "pos_config", "is_trusting", "is_trusted")
