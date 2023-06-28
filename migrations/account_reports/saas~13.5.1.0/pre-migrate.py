# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "tax_closing_end_date", "date")
    query = "UPDATE account_move SET tax_closing_end_date = date WHERE is_tax_closing"
    util.explode_execute(cr, query, table="account_move")

    util.remove_field(cr, "account.move", "is_tax_closing")
    util.remove_model(cr, "account.multicurrency.revaluation.report")
