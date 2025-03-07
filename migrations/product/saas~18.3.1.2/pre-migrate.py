from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "uom.uom", "packaging_barcodes_count")


def set_product_manager(cr, from_group):
    cr.execute(
        """
        INSERT INTO res_groups_users_rel
             SELECT %s AS gid, uid
               FROM res_groups_users_rel
              WHERE gid = %s
        ON CONFLICT DO NOTHING
        """,
        [util.ref(cr, "product.group_product_manager"), util.ref(cr, from_group)],
    )
