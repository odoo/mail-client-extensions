from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "uom.uom", "packaging_barcodes_count")

    util.move_field_to_module(cr, "product.tag", "visible_on_ecommerce", "website_sale", "product")
    util.rename_field(cr, "product.tag", "visible_on_ecommerce", "visible_to_customers")
    util.move_field_to_module(cr, "product.tag", "image", "website_sale", "product")


def set_product_manager(cr, from_group):
    cr.execute(
        """
        INSERT INTO res_groups_users_rel(gid, uid)
             SELECT %s AS gid, uid
               FROM res_groups_users_rel
              WHERE gid = %s
        ON CONFLICT DO NOTHING
        """,
        [util.ref(cr, "product.group_product_manager"), util.ref(cr, from_group)],
    )
