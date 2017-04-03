# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'print.document.partner.wizard', 'currency_id', 'provider_currency_id')
