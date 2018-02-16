# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'sale.config.settings', 'default_print_provider', 'default_provider_id')
