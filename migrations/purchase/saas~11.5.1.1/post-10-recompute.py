from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        UPDATE purchase_order_line l
           SET product_uom_qty = l.product_qty
          FROM product_product p, product_template t
         WHERE p.id = l.product_id
           AND t.id = p.product_tmpl_id
           AND t.uom_id = l.product_uom
    """)
    # behave somewhat like purchase: if the uoms are not in the same category
    # then we say that the quantity is the same (as if we had called _compute_quantity
    # on the uom with raise_if_failure=False); otherwise it will raise a shitload of errors
    # for data in the past for a field that seems only to be there for reporting purposes...
    cr.execute("""
        UPDATE purchase_order_line l
           SET product_uom_qty = l.product_qty
          FROM product_product p, product_template t,
               uom_uom u1, uom_uom u2
         WHERE p.id = l.product_id
           AND t.id = p.product_tmpl_id
           AND t.uom_id != l.product_uom
           AND u1.category_id != u2.category_id
           AND u1.id = l.product_uom
           AND u2.id = t.uom_id
    """)
    # lines with uom different than the one on the product template but in a compatible
    # category: let the orm recompute
    query = "SELECT id FROM purchase_order_line WHERE product_uom_qty IS NULL"
    util.recompute_fields(cr, "purchase.order.line", ["product_uom_qty"], query=query)
