# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "payment.transaction", "invoice_id")
    util.remove_view(cr, "sale_subscription.transaction_form")
