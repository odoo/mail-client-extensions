# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)

    uom = util.ref(cr, "uom.product_uom_hour")
    if not uom:
        uom = env["uom.uom"].search([("measure_type", "=", "time"), ("uom_type", "=", "reference")], limit=1).id
    if not uom:
        uom = env["uom.uom"].search([("measure_type", "=", "time")], limit=1).id
    cr.execute("UPDATE res_company SET timesheet_encode_uom_id=%s", [uom])
