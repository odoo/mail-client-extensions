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
        WHERE amount = 0 AND amount_type = 'percent' AND id in 
            (SELECT child_tax from account_tax_filiation_rel where parent_tax IS NOT NULL)
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

    # Since we moved some tax to their parent and set them as inactive, we need to change those on the account_move_line for
    # The field tax_line_id and tax_line_ids
    cr.execute("""UPDATE account_move_line aml
                    SET tax_line_id = tax.parent_id
                    FROM account_tax tax
                    WHERE tax.id = aml.tax_line_id 
                        AND tax.active = false 
                        AND tax.amount_type = 'percent' 
                        AND tax.parent_id IS NOT NULL
                """)

    cr.execute("""UPDATE account_move_line_account_tax_rel a
                    SET account_tax_id = tax.parent_id
                    FROM account_tax tax
                    WHERE tax.id = a.account_tax_id 
                        AND tax.active = false 
                        AND tax.amount_type = 'percent' 
                        AND tax.parent_id IS NOT NULL
                """)