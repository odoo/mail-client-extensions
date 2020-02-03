# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("UPDATE ir_rule SET active = true WHERE id = %s", [util.ref(cr, "delivery.delivery_carrier_comp_rule")])

    util.remove_view(cr, "delivery.assets_backend")
