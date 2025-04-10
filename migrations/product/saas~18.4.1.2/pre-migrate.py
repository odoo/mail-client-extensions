from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT id
          FROM product_supplierinfo
         WHERE product_id IS NULL
           AND product_tmpl_id IS NULL
        """
    )
    if cr.rowcount:
        util.remove_records(cr, "product.supplierinfo", [iid for (iid,) in cr.fetchall()])
    util.explode_execute(
        cr,
        """
        UPDATE product_supplierinfo psi
           SET product_tmpl_id = pp.product_tmpl_id
          FROM product_product pp
         WHERE psi.product_id = pp.id
           AND psi.product_tmpl_id IS NULL
        """,
        table="product_supplierinfo",
        alias="psi",
    )
    util.create_column(cr, "product_supplierinfo", "product_uom_id", "int4")
    util.explode_execute(
        cr,
        """
        UPDATE product_supplierinfo psi
               SET product_uom_id = pt.uom_id
              FROM product_template pt
             WHERE psi.product_tmpl_id = pt.id
               AND psi.product_uom_id IS NULL
            """,
        table="product_supplierinfo",
        alias="psi",
    )
