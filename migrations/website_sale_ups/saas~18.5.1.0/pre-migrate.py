from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_ups.res_config_settings_view_form")
