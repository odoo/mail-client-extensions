# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "fleet_vehicle", "first_contract_date", "date")

    cr.execute("ALTER TABLE fleet_vehicle DROP CONSTRAINT driver_id_unique")
