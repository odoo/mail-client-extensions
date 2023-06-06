# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    for model in ("account.report.column", "account.report.expression"):
        util.change_field_selection_values(cr, model, "figure_type", {"monetary_without_symbol": "monetary"})
