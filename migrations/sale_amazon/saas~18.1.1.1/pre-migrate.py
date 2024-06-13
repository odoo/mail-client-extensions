from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE res_partner
           SET email = amazon_email
         WHERE email IS NULL
           AND amazon_email IS NOT NULL
        """,
        table="res_partner",
    )
    util.update_field_usage(cr, "res.partner", "amazon_email", "email")
    util.remove_field(cr, "res.partner", "amazon_email")
    util.remove_field(cr, "amazon.account", "is_follow_up_displayed")
    util.remove_record(cr, "sale_amazon.list_amazon_marketplace_action")
