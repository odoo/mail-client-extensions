# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "delivery_carrier", "ups_duty_payment", "varchar")

    cr.execute("UPDATE delivery_carrier SET ups_duty_payment='RECIPIENT'")
