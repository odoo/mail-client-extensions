# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.payment.method", "adyen_payout_id")
    util.remove_record(cr, "pos_adyen.access_adyen_payout_group_pos_manager")

    if util.table_exists(cr, "adyen_transaction"):
        util.create_column(cr, "adyen_transaction", "pos_payment_id", "int4")
        util.create_column(cr, "adyen_transaction", "pos_order_id", "int4")
