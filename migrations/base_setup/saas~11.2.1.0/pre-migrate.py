# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'res.config.settings', 'default_user_rights', 'user_default_rights')
    util.rename_field(cr, 'res.config.settings', 'default_external_email_server', 'external_email_server_default')

    util.remove_field(cr, 'res.config.settings', 'default_custom_report_footer')
    cr.execute("DELETE FROM ir_config_parameter WHERE key='base_setup.default_custom_report_footer'")
