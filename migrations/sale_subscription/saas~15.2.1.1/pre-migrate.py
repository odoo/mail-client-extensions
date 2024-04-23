from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(cr, "sale_subscription", "sale_subscription_uuid_uniq")
    util.rename_field(cr, "sale.subscription", "uuid", "access_token")
    util.rename_field(cr, "sale.subscription", "website_url", "access_url")
