# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "lunch_alert", "name", "varchar")
    cr.execute("UPDATE lunch_alert SET name=CONCAT('Alert ', id)")
