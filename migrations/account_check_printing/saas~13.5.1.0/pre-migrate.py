# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, 'account.payment', 'check_number_int')
    util.create_column(cr, 'account_move', 'preferred_payment_method_id', 'int4')
