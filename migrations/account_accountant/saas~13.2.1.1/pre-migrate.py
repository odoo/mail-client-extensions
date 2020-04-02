# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "payment_state_before_switch", "varchar")
    util.create_column(cr, "account_payment", "state_before_switch", "varchar")
    util.create_column(cr, "res_company", "invoicing_switch_threshold", "date")

    util.remove_field(cr, "account.payment", "attachment_ids")
    util.remove_field(cr, "account.bank.statement", "attachment_ids")
