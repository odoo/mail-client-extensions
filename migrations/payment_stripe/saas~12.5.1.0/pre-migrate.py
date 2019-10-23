# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "payment_transaction", "stripe_payment_intent", "varchar")
    util.create_column(cr, "payment_transaction", "stripe_payment_intent_secret", "varchar")
    util.create_column(cr, "payment_token", "stripe_payment_method", "varchar")
