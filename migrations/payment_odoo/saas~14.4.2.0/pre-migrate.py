# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "payment.acquirer", "odoo_adyen_payout_id")
