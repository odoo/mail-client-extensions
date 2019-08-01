# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "ocn_push_notification")
    cr.execute("DELETE FROM ir_config_parameter WHERE key='ocn.ocn_push_notification'")
    util.remove_view(cr, "ocn_client.res_config_settings_view_form")
