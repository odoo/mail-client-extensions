# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_batch_payment", 'sdd_batch_booking', 'boolean')

    cr.execute("UPDATE account_batch_payment SET sdd_batch_booking=TRUE")
