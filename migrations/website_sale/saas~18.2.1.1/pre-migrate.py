from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_sale.mail_template_sale_cart_recovery", util.update_record_from_xml)
    util.remove_view(cr, "website_sale.add_to_cart_redirect")

    util.remove_record(cr, "website_sale.s_dynamic_snippet_products_000_js")
    util.remove_record(cr, "website_sale.s_popup_000_js")
