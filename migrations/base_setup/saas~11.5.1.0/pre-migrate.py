# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "external_report_layout")
    cr.execute("DELETE FROM ir_config_parameter WHERE key='base_setup.external_report_layout'")
