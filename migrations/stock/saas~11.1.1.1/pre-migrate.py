# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'stock_quant_package', 'location_id', 'int4')
    util.create_column(cr, 'stock_quant_package', 'company_id', 'int4')

    # as quants does not have any order, take one randomly to update package
    cr.execute("""
        UPDATE stock_quant_package p
           SET location_id = q.location_id, company_id = q.company_id
          FROM stock_quant q
         WHERE p.id = q.package_id
    """)

    noup = util.splitlines("""
        stock_location_stock
        stock_location_company
        stock_location_output
        location_pack_zone
        picking_type_internal
        picking_type_in
        picking_type_out

        # demo data
        chi_picking_type_in
        chi_picking_type_out
        stock_location_shop0
    """)
    for name in noup:
        util.force_noupdate(cr, 'stock.' + name, True)
