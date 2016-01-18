# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def findline(move, linezero=False, tax_amount=0.0):
    for line in move.line_ids:
        if linezero and line.debit == line.credit: #only case where it happens is when debit=credit=0
            return line
        elif not linezero and line.tax_amount == tax_amount:
            return line
    return False

def findtax(code1, code2, base=True):
    code = [code1, code2]
    cr.execute("""SELECT parent_id 
                    FROM (SELECT parent_id, count(*) 
                        FROM account_tax 
                        WHERE parent_id IS NOT NULL
                            AND %s in %s) AS e
                    WHERE e.count > 1
                """, ('base_code_id' if base else 'tax_code_id', tuple(code)))
    tax = cr.dictfetchone()
    if tax:
        return tax['parent_id']
    # Try finding for a refund instead
    r.execute("""SELECT parent_id 
                    FROM (SELECT parent_id, count(*) 
                        FROM account_tax 
                        WHERE parent_id IS NOT NULL
                            AND %s in %s) AS e
                    WHERE e.count > 1
                """, ('ref_base_code_id' if base else 'ref_tax_code_id', tuple(code)))
    tax = cr.dictfetchone()
    if tax:
        return tax['parent_id']
    return False


def migrate(cr, version):
    env = util.env(cr)

    # Some tax assignation on account_move_line have been wrongly computed, the way to fix those is the following:
    # if one of the line (line0) in an account_move has a debit=credit=0, take the tax_amount of that line, find the other
    # line in that account_move with the same tax_amount, if that line has a tax_line_id: the tax referenced by that should 
    # be a tax with 2 children, one with base/tax_code_id = line.tax_code_id and the other with base/tax_code_id = line0.tax_code_id
    cr.execute("""SELECT DISTINCT(move_id) AS id 
                    FROM account_move_line 
                    WHERE debit = 0 
                        AND credit = 0 
                        AND tax_code_id IS NOT NULL 
                        AND tax_amount IS NOT NULL""")

    move_ids = cr.dictfetchall()
    tax_line_ids_to_update = []
    tax_line_id_to_update = []
    for move in env['account.move'].browse(move_ids):
        line0 = findline(move, linezero=True)
        line = findline(move, line0.tax_amount)
        if not line:
            continue
        #Update tax_line_id
        if line.tax_line_id:
            tax = findtax(line.tax_code_id, line0.tax_code_id, base=False)
            if tax:
                tax_line_id_to_update.append((line.id, tax))
        #Update tax_line_ids
        else:
            tax = findtax(line.tax_code_id, line0.tax_code_id, base=True)
            if tax:
                tax_line_ids_to_update.append((line.id, tax))

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