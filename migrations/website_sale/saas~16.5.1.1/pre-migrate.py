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

        # In multi-website environments, cowed views were created for each
        # website that had this setting enabled. Here we only create "extra_info"
        # views based on existing "extra_info_option" views. The arch will be set in
        # a post script so that it's up to date.
        cr.execute(
            """
            INSERT INTO ir_ui_view (
                name, key, active,
                priority, mode, type, website_id
            )
            SELECT
                'Checkout Extra Info', 'website_sale.extra_info', active,
                16, 'primary', 'qweb', website_id
              FROM ir_ui_view
             WHERE key = 'website_sale.extra_info_option'
               AND website_id IS NOT NULL
               AND active
            """,
        )

    util.remove_field(cr, "res.config.settings", "module_website_sale_digital")
    util.remove_view(cr, "website_sale.cart_popover")
    util.remove_view(cr, "website_sale.cart_summary")
    util.remove_view(cr, "website_sale.extra_info_option")
    util.remove_view(cr, "website_sale.payment_sale_note")
    util.remove_view(cr, "website_sale.payment_footer")
    util.remove_view(cr, "website_sale.short_cart_summary")
