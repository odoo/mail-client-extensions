# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
        INSERT INTO mrp_document(ir_attachment_id, priority, active)
             SELECT a.id, a.priority, true
               FROM ir_attachment a, mrp_bom_line l
              WHERE a.model = 'product.product'
                AND a.res_id = l.product_id
              UNION
             SELECT a.id, a.priority, true
               FROM ir_attachment a, mrp_bom_line l, product_product p
              WHERE a.model = 'product.template'
                AND p.id = l.product_id
                AND a.res_id = p.product_tmpl_id
    """)
