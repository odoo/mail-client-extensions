# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for p in ['old', 'new']:
        util.create_column(cr, 'mrp_eco_bom_change', p + '_uom_id', 'int4')
        cr.execute("""
            UPDATE mrp_eco_bom_change
               SET {0}_uom_id = product_uom_id
             WHERE COALESCE({0}_product_qty, 0) != 0
        """.format(p))
    util.remove_field(cr, 'mrp.eco.bom.change', 'product_uom_id')

    util.remove_view(cr, 'mrp_plm.mrp_eco_tag_view_form')

    # create mrp.document
    cr.execute("""
        INSERT INTO mrp_document(ir_attachment_id, priority, active)
             SELECT id, priority, true
               FROM ir_attachment
              WHERE res_model = 'mrp.eco'
    """)
    cr.execute("ALTER TABLE mrp_eco DROP CONSTRAINT mrp_eco_displayed_image_id_fkey")
    cr.execute("""
        WITH _up AS (
            UPDATE mrp_eco e
               SET displayed_image_id = d.id
              FROM mrp_document d
             WHERE d.ir_attachment_id = e.displayed_image_id
         RETURNING e.id
        )
        UPDATE mrp_eco
           SET displayed_image_id = NULL
         WHERE id NOT IN (SELECT id FROM _up)
    """)

    util.rename_field(cr, 'mrp.eco', 'attachment_count', 'mrp_document_count')
    util.rename_field(cr, 'mrp.eco', 'attachment_ids', 'mrp_document_ids')
