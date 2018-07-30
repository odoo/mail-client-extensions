# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def change_categ(cr, xid, measure):
    uom_id = util.rename_xmlid(cr, "product." + xid, "uom." + xid)
    if uom_id:
        cr.execute("UPDATE uom_category SET measure_type=%s WHERE id=%s", [measure, uom_id])

def migrate(cr, version):
    util.rename_model(cr, 'product.uom', 'uom.uom')
    util.rename_model(cr, "product.uom.categ", "uom.category")
    util.create_column(cr, "uom_uom", "measure_type", "varchar")
    util.create_column(cr, "uom_category", "measure_type", "varchar")

    change_categ(cr, "product_uom_categ_unit", "unit")
    change_categ(cr, "product_uom_categ_kgm", "weight")
    change_categ(cr, "uom_categ_wtime", "time")
    change_categ(cr, "uom_categ_length", "length")
    change_categ(cr, "product_uom_categ_vol", "volume")

    cr.execute("""
        UPDATE uom_uom u
           SET measure_type = c.measure_type
          FROM uom_category c
         WHERE c.id = u.category_id
    """)

    # only one reference uom is allowed per category
    # Change type and let xml data updates them
    cr.execute("""
        WITH multiple_references AS (
            SELECT unnest((array_agg(id order by id))[2:array_length(array_agg(id), 1)]) as id
              FROM uom_uom
             WHERE uom_type='reference'
          GROUP BY category_id
            HAVING count(id) > 1
        )
        UPDATE uom_uom
           SET uom_type='bigger', factor=1
         WHERE id IN (SELECT id FROM multiple_references)
    """)

    eb = util.expand_braces
    units = "unit dozen kgm gram day hour ton meter km cm litre "\
            "lb oz inch foot mile floz qt gal"
    for unit in units.split():
        util.rename_xmlid(cr, *eb("{product,uom}.product_uom_" + unit))

    for suffix in "tree_view form_view form_action".split():
        util.rename_xmlid(cr, *eb("{product,uom}.product_uom_" + suffix))
        util.rename_xmlid(cr, *eb("{product,uom}.product_uom_categ_" + suffix))

    util.rename_xmlid(cr, "product.access_product_uom_categ_user", "uom.access_uom_category_user")
    util.rename_xmlid(cr, "product.access_product_uom_user", "uom.access_uom_uom_user")
    util.rename_xmlid(cr, *eb("{product,uom}.group_uom"))
