from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "product.supplierinfo", "product_uom", "product_uom_id")
    util.rename_field(cr, "product.pricelist.item", "product_uom", "product_uom_name")
    cr.execute("ALTER TABLE product_template ALTER COLUMN categ_id DROP NOT NULL")
    # This will allow `delete_unused` to correctly remove related data if not used.
    util.remove_constraint(cr, "product_template", "product_template_categ_id_fkey")
    cr.execute("""
        ALTER TABLE product_template
          ADD CONSTRAINT product_template_categ_id_fkey
           FOREIGN KEY (categ_id) REFERENCES product_category(id)
            ON DELETE SET NULL
    """)
    util.delete_unused(cr, *[f"product.product_category_{cat}" for cat in ("1", "2", "4", "5", "6", "all")])
    util.rename_xmlid(cr, "product.product_category_3", "product.product_category_services")
    util.rename_xmlid(cr, "product.cat_expense", "product.product_category_expenses")
