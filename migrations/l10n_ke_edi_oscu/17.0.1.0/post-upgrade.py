from odoo.upgrade import util


def migrate(cr, version):
    query = cr.mogrify(
        """
            UPDATE product_product p
               SET l10n_ke_packaging_unit_id = %s
              FROM product_template t
             WHERE t.id = p.product_tmpl_id
               AND t.detailed_type = 'service'
        """,
        [util.ref(cr, "l10n_ke_edi_oscu.packaging_type_ou")],
    ).decode()
    util.explode_execute(cr, query, table="product_product", alias="p")
