# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def findtax(cr, code1, code2, base, cache):
    codes = (code1, code2)
    key = (frozenset(codes), base)
    if key in cache:
        return cache[key]

    col = 'base_code_id' if base else 'tax_code_id'
    for prefix in ['', 'ref_']:
        cr.execute("""
            SELECT parent_id
              FROM account_tax
             WHERE parent_id IS NOT NULL
               AND {0} IN %s
          GROUP BY parent_id
            HAVING count(*) > 1
        """.format(prefix + col), [codes])
        tax = cr.fetchone()
        if tax:
            cache[key] = tax[0]
            return tax[0]
    cache[key] = None
    return None

def migrate(cr, version):
    env = util.env(cr)

    # Some tax assignation on account_move_line have been wrongly computed, the way to fix those is the following:
    # if one of the line (line0) in an account_move has a debit=credit=0, take the tax_amount of that line, find the other
    # line in that account_move with the same tax_amount, if that line has a tax_line_id: the tax referenced by that should
    # be a tax with 2 children, one with base/tax_code_id = line.tax_code_id and the other with base/tax_code_id = line0.tax_code_id

    tax_line_ids_to_update = []
    tax_line_id_to_update = []
    tax_cache = {}
    cr.execute("""
        WITH lines0 AS (
            SELECT id, move_id, tax_code_id, tax_amount
              FROM account_move_line
             WHERE credit = 0
               AND debit = 0
               AND tax_amount IS NOT NULL
               AND tax_code_id IS NOT NULL
        )
        SELECT l1.id, l0.tax_code_id, l1.tax_code_id, l1.tax_line_id
          FROM account_move_line l1
          JOIN lines0 l0 ON (l1.id != l0.id AND l0.move_id=l1.move_id)
         WHERE l0.tax_amount = l1.tax_amount
           AND l1.tax_code_id IS NOT NULL
    """)
    for line_id, tax_code1, tax_code2, tax_line_id in cr.fetchall():
        if tax_line_id:
            # Update tax_line_id
            tax = findtax(cr, tax_code1, tax_code2, base=False, cache=tax_cache)
            if tax:
                tax_line_id_to_update.append((line_id, tax))
        else:
            # Update tax_line_ids
            tax = findtax(cr, tax_code1, tax_code2, base=True, cache=tax_cache)
            if tax:
                tax_line_ids_to_update.append((line_id, tax))

    for tuple_update in tax_line_ids_to_update:
        cr.execute("""UPDATE account_move_line_account_tax_rel
                        SET account_tax_id = %s
                        WHERE account_move_line_id = %s
                    """, (tuple_update[1], tuple_update[0]))

    for tuple_update in tax_line_id_to_update:
        cr.execute("""UPDATE account_move_line
                        SET tax_line_id = %s
                        WHERE id = %s
                    """, (tuple_update[1], tuple_update[0]))

    # Finish migration on tax: if only one child, deactivate child and put value on parent

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

    ids_to_get_account = []
    for parent_tax in env['account.tax'].search([('amount_type', '=', 'group')]):
        childs = parent_tax.children_tax_ids.filtered(lambda t: t.active)
        if len(childs) == 1:
            parent_tax.amount_type = 'percent'
            parent_tax.amount = childs.amount
            parent_tax.account_id = childs.account_id
            parent_tax.refund_account_id = childs.refund_account_id
            childs.active = False
        if len(childs) == 0:
            parent_tax.amount_type = 'percent'
            parent_tax.amount = 0
            ids_to_get_account.append(parent_tax.id)
    if ids_to_get_account:
        cr.execute("""UPDATE account_tax t
                        SET account_id = t2.account_id,
                            refund_account_id = t2.refund_account_id
                        FROM account_tax t2
                        WHERE t2.parent_id = t.id
                            AND t.id IN %s
                    """, (tuple(ids_to_get_account),))

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
