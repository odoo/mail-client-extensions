from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale.add_to_cart_redirect")

    util.remove_record(cr, "website_sale.s_dynamic_snippet_products_000_js")
    util.remove_record(cr, "website_sale.s_popup_000_js")

    util.remove_field(cr, "website", "all_pricelist_ids")
    util.remove_field(cr, "website", "fiscal_position_id")
    util.remove_field(cr, "website", "pricelist_id")
    util.remove_field(cr, "res.partner", "last_website_so_id")
