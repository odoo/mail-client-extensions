# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        UPDATE delivery_carrier
           SET dhl_package_dimension_unit=left(dhl_package_dimension_unit, 1),
               dhl_package_weight_unit=left(dhl_package_weight_unit, 1)
    """)
