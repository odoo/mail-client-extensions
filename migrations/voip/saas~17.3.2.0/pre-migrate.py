from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "voip.res_config_settings_view_form")

    util.remove_field(cr, "res.config.settings", "wsServer")
    util.remove_field(cr, "res.config.settings", "pbx_ip")
    util.remove_field(cr, "res.config.settings", "mode")
