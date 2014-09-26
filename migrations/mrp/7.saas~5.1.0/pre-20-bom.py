# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    '''
        In 7.0: a BoM can have a Parent (also BoM) and can have children (bom_lines: also BoM)
                (at the same time, does not need to pass through product apparently)
        In 8.0: a BoM has no parent but has BoM lines (mrp_bom_line) as children
                A BoM can also only have a product_tmpl_id instead of product_id
                (just need to set product_tmpl_id as it is required)
    '''

    if not util.table_exists(cr, 'mrp_bom_line'):
        cr.execute("""CREATE TABLE mrp_bom_line(
                        id SERIAL NOT NULL,
                        type varchar,
                        product_id int,
                        product_uos_qty float,
                        product_uos int,
                        product_qty float,
                        product_uom int,
                        date_start date,
                        date_stop date,
                        sequence int,
                        routing_id int,
                        product_rounding float,
                        product_efficiency float,
                        bom_id int,
                        PRIMARY KEY(id)
                      )
                   """)
    # Create MRP BoM Lines for everything that has a parent
    cr.execute("""
        INSERT INTO mrp_bom_line (type, product_id, product_uos_qty, product_uos, product_qty,
                                  product_uom, date_start, date_stop, sequence,
                                  routing_id, product_rounding, product_efficiency, bom_id)
        (SELECT type, product_id, product_uos_qty, product_uos, product_qty,
                product_uom, date_start, date_stop, sequence,
                routing_id, product_rounding, product_efficiency, bom_id
           FROM mrp_bom WHERE bom_id IS NOT NULL)
    """)

    # Delete all BoMs with a parent but without children
    cr.execute("""
        DELETE FROM mrp_bom
         WHERE bom_id IS NOT NULL
           AND NOT EXISTS (SELECT 1 FROM mrp_bom b2 where b2.bom_id = mrp_bom.id)
     RETURNING id
    """)

    bom_ids = tuple(x[0] for x in cr.fetchall())
    if bom_ids:
        cr.execute('DELETE FROM ir_model_data WHERE model=%s AND res_id IN %s',
                   ['mrp.bom', bom_ids])

    # Create extra field product_tmpl_id in mrp_bom and fill it in as the template of product_id

    util.create_column(cr, 'mrp_bom', 'product_tmpl_id', 'int')

    cr.execute("""
        UPDATE mrp_bom
           SET product_tmpl_id = pp.product_tmpl_id
          FROM product_product pp
         WHERE mrp_bom.product_id = pp.id
    """)
