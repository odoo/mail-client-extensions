# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "delivery_carrier", "fedex_duty_payment", "varchar")

    cr.execute("UPDATE delivery_carrier SET fedex_duty_payment='SENDER'")
