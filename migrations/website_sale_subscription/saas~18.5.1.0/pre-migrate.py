from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_subscription.accordion_subscription_item")
    util.remove_view(cr, "website_sale_subscription.pricing_table")
