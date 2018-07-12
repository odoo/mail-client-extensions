# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "resource_calendar_leaves", "time_type", "varchar")
    cr.execute("UPDATE resource_calendar_leaves SET time_type='leave'")
