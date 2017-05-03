# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pos_configs = util.env(cr)['pos.config'].search([('customer_facing_display_html', '=', False)])
    default_values = pos_configs.default_get(['customer_facing_display_html'])
    pos_configs.write(default_values)
