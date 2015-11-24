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

    cr.execute("""UPDATE account_tax
        SET active = false
        WHERE amount = 0 AND amount_type = 'percent' AND id in (SELECT child_tax from account_tax_filiation_rel where parent_tax IS NOT NULL)
        """)

    env = util.env(cr)

    for parent_tax in env['account.tax'].search([('amount_type', '=', 'group')]):
        childs = parent_tax.children_tax_ids.filtered(lambda t: t.active)
        if len(childs) == 1:
            parent_tax.amount_type = 'percent'
            parent_tax.amount = childs.amount
            childs.active = False
        if len(childs) == 0:
            parent_tax.amount_type = 'percent'
            parent_tax.amount = 0
