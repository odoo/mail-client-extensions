# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_account', 'deprecated', 'boolean')

    cr.execute("""UPDATE account_account
        SET deprecated = NOT active
        """)
