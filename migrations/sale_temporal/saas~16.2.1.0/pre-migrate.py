# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "sale.temporal.recurrence", "subscription_unit_display", "temporal_unit_display")
