from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_subscription.product_subscriptions")
