# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        UPDATE stock_location
           SET usage='internal'
         WHERE usage='procurement'
    """)
    cr.execute("""
        UPDATE stock_location s
           SET name=concat(coalesce(s.name,''),' / ',coalesce(p.name,'')),
               complete_name=concat(coalesce(s.complete_name,''),' / ',coalesce(p.name,''))
          FROM res_partner p
         WHERE s.partner_id IS NOT NULL
           AND s.partner_id=p.id
    """)
    #Recompute complete_names of the childs?

    util.remove_field(cr, 'stock.location', 'partner_id')

    util.create_column(cr, 'stock_move_line', 'company_id', 'int4')
    cr.execute("""
        UPDATE stock_move_line l
           SET company_id=m.company_id
          FROM stock_move m
         WHERE l.move_id=m.id
    """)

    util.remove_field(cr, "stock.package_level", "picking_source_location")
    util.remove_record(cr, 'stock.property_stock_inventory')
    util.remove_record(cr, 'stock.property_stock_production')

    util.remove_view(cr, "stock.view_template_property_form")

    util.force_noupdate(cr, 'stock.stock_location_scrapped')
    util.force_noupdate(cr, 'stock.location_inventory')
    util.force_noupdate(cr, 'stock.location_procurement')
    util.force_noupdate(cr, 'stock.location_production')
