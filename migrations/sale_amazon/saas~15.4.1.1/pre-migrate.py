from odoo.upgrade import util


def migrate(cr, version):
    # No data upgrade or announcement is needed as the old API will stop working in July 2022. Customers should have installed
    # `sale_amazon_spapi` to continue using the Amazon integration.
    util.remove_field(cr, "amazon.account", "auth_token")
    util.remove_field(cr, "amazon.marketplace", "code")

    cr.execute("""UPDATE amazon_marketplace SET name = domain""")

    util.remove_field(cr, "amazon.offer", "domain")
    util.remove_field(cr, "amazon.marketplace", "domain")

    util.remove_view(cr, "sale_amazon.amazon_account_view_form_inherit")
    util.remove_view(cr, "sale_amazon.amazon_account_view_search_inherit")
    util.remove_view(cr, "sale_amazon.amazon_marketplace_view_form_inherit")
    util.remove_view(cr, "sale_amazon.amazon_marketplace_view_tree_inherit")
    util.remove_view(cr, "sale_amazon.amazon_offer_view_search_inherit")
