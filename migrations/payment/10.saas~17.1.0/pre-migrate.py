# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'payment_acquirer', 'capture_manually', 'boolean')
    cr.execute("UPDATE payment_acquirer SET capture_manually = (auto_confirm='authorize')")
