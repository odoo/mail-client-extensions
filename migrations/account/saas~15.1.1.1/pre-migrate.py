# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.payment.register", "hide_payment_method_line")
    util.remove_field(cr, "account.payment", "hide_payment_method_line")
