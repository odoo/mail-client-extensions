from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_management.res_config_settings_view_form_inherit_sale_management")
