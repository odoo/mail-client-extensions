# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # as we are now using active state from "website_sale.extra_info" view
    # itself instead of the one from "website_sale.extra_info_option" to
    # check if we need to redirect user to /shop/extra_info step, so we must
    # copy former view "active" value to new one
    extra_info_option_view_id = util.ref(cr, "website_sale.extra_info_option")
    extra_info_view_id = util.ref(cr, "website_sale.extra_info")
    if extra_info_option_view_id and extra_info_view_id:
        cr.execute(
            """
            UPDATE ir_ui_view
               SET active = (SELECT active FROM ir_ui_view WHERE id = %s)
            WHERE id = %s
        """,
            (extra_info_option_view_id, extra_info_view_id),
        )

    util.remove_field(cr, "res.config.settings", "module_website_sale_digital")
    util.remove_view(cr, "website_sale.cart_popover")
    util.remove_view(cr, "website_sale.cart_summary")
    util.remove_view(cr, "website_sale.extra_info_option")
    util.remove_view(cr, "website_sale.payment_sale_note")
    util.remove_view(cr, "website_sale.payment_footer")
    util.remove_view(cr, "website_sale.short_cart_summary")
