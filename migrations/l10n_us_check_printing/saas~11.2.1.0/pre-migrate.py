# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for suffix in 'layout multi_stub margin_top margin_left'.split():
        field = 'us_check_' + suffix
        util.remove_field(cr, 'res.company', field)
        util.remove_field(cr, 'res.config.settings', field)
    util.remove_view(cr, 'l10n_us_check_printing.res_config_settings_view_form')
