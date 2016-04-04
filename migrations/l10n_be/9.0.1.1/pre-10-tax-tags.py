# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # keep current name before update from data files.
    util.create_column(cr, 'account_tax_template', '_old_name', 'varchar')
    cr.execute("UPDATE account_tax_template SET _old_name=name")
