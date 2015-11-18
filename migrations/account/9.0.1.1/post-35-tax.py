# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    group_id = util.ref(cr, 'account.tax_group_taxes')

    cr.execute("""UPDATE account_tax
    SET tax_group_id = %s
    """, (group_id,))

    cr.execute("""DELETE FROM account_tax_group
        WHERE name='migration'
        """)
