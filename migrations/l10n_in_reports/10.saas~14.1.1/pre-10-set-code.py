# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""select name from ir_model_data where model='account.financial.html.report.line' and module='l10n_in_reports'""")
    for name in cr.fetchall():
        util.remove_record(cr, 'l10n_in_reports.' + name[0])

