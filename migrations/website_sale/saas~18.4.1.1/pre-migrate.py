from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "website_sale.product_custom_text", "website_sale.product_terms_and_conditions")
    cr.execute(
        """
        UPDATE ir_ui_view
           SET inherit_id = NULL,
               mode = 'primary'
         WHERE id = %s
        """,
        [util.ref(cr, "website_sale.product_terms_and_conditions")],
    )

    util.remove_field(cr, "res.config.settings", "group_delivery_invoice_address")
    hid = util.ref(cr, "account.group_delivery_invoice_address")
    if not hid:
        return

    ptl = util.ref(cr, "base.group_portal")
    pub = util.ref(cr, "base.group_public")

    cr.execute(
        """
        DELETE FROM res_groups_implied_rel
              WHERE hid = %s
                AND gid IN %s
        """,
        (hid, (ptl, pub)),
    )
