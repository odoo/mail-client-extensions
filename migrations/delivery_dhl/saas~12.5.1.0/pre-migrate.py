# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "delivery_carrier", "dhl_duty_payment", "varchar")

    cr.execute("UPDATE delivery_carrier SET dhl_duty_payment='S'")
