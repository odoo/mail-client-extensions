# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "sale_subscription.payment_transaction_salesman_rule")
    util.remove_record(cr, "sale_subscription.payment_token_salesman_rule")
    cr.execute("DELETE FROM ir_translation WHERE name='sale.subscription,health' AND type='selection'")
