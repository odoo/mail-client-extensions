from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_loyalty.pay_with_gift_card_form")
    util.remove_view(cr, "website_sale_loyalty.loyalty_generate_wizard_view_form_inherit_website_sale_loyalty")

    util.remove_field(cr, "loyalty.generate.wizard", "website_id")
