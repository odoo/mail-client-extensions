from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "pos.category", "child_id", "child_ids")
    util.remove_field(cr, "pos.session", "cash_register_total_entry_encoding")
    util.create_column(cr, "pos_config", "customer_display_type", "varchar")
    where_clause = util.SQLStr(
        "iface_display_id IS NOT NULL"
        if util.module_installed(cr, "pos_iot")
        else "iface_customer_facing_display_via_proxy = True"
    )
    cr.execute(util.format_query(cr, "UPDATE pos_config SET customer_display_type = 'proxy' WHERE {}", where_clause))
    cr.execute("UPDATE pos_config SET customer_display_type = 'local' WHERE iface_customer_facing_display_local = True")
    util.rename_field(
        cr,
        "res.config.settings",
        "pos_iface_customer_facing_display_background_image_1920",
        "pos_customer_display_bg_img",
    )
    util.remove_field(cr, "res.config.settings", "pos_iface_customer_facing_display_via_proxy")
    util.remove_field(cr, "res.config.settings", "pos_iface_customer_facing_display_local")
    util.remove_column(cr, "res_config_settings", "pos_proxy_ip")
    util.rename_field(
        cr, "pos.config", "iface_customer_facing_display_background_image_1920", "customer_display_bg_img"
    )
    util.remove_field(cr, "pos.config", "iface_customer_facing_display_via_proxy")
    util.remove_field(cr, "pos.config", "iface_customer_facing_display_local")
    util.remove_field(cr, "pos.config", "iface_customer_facing_display")
    util.remove_view(cr, "point_of_sale.account_product_template_form_view")
