# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for m in 'top middle bottom'.split():
        util.delete_model(cr, 'report.l10n_us_check_printing.print_check_' + m, drop_table=False)
