# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "maintenance_equipment", "effective_date", "date")

    cr.execute("UPDATE maintenance_equipment set effective_date=create_date::date")
    util.rename_field(cr, "maintenance.request", "technician_user_id", "user_id")
