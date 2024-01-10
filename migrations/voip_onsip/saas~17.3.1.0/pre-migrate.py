from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "voip_onsip.res_config_settings_view_form")
