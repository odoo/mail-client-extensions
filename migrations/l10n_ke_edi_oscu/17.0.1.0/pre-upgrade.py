from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_partner", "l10n_ke_branch_code", "varchar", default="00")
    util.create_column(cr, "product_product", "l10n_ke_packaging_unit_id", "int4")
    util.create_column(cr, "product_product", "l10n_ke_product_type_code", "varchar")

    query = """
        UPDATE product_product p
          SET l10n_ke_product_type_code = '3'
         FROM product_template t
        WHERE t.id = p.product_tmpl_id
          AND t.type = 'service'
    """
    util.explode_execute(cr, query, table="product_product", alias="p")
