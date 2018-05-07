# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

# NOTE: this script is simlinked in saas~11.1

def migrate(cr, version):
    for field in 'model function args'.split():
        util.remove_field(cr, 'ir.cron', field)
