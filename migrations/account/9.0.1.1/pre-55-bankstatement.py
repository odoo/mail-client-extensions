# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""UPDATE account_bank_statement
        SET state = 'open'
        WHERE state = 'draft'
        """)
