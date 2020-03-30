# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "sale.report", "days_to_confirm", "avg_days_to_confirm")
