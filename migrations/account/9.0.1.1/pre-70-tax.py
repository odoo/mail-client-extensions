# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
        Migrate account.tax
    """

    util.create_column(cr, 'account_tax', 'analytic', 'bool')

    cr.execute("""UPDATE account_tax
        SET analytic = true
        WHERE account_analytic_collected_id is not null or account_analytic_paid_id is not null
        """)

    cr.execute("""UPDATE account_tax
        SET active = false, type = 'percent'
        WHERE type = 'none' or type = 'balance'
        """)  # needs to be done manually

    cr.execute("""UPDATE account_tax
        SET python_applicable = 'result = True'
        WHERE python_applicable IS NULL
        """)

    cr.execute("""UPDATE account_tax
        SET amount = 100 * amount where type = 'percent'
        """)

    cr.execute("""UPDATE account_tax
                    SET type = 'group',
                        amount = '0'
                    WHERE id IN (SELECT DISTINCT(t.parent_id) FROM account_tax t where t.parent_id is not null)""")

    util.create_m2m(cr, 'account_tax_filiation_rel',
                    'account_tax', 'account_tax', 'parent_tax', 'child_tax')

    cr.execute("""INSERT INTO account_tax_filiation_rel(parent_tax, child_tax)
        SELECT parent_id, id
        FROM account_tax
        WHERE parent_id IS NOT NULL
        """)

    util.create_column(cr, 'account_tax', 'tax_group_id', 'int4')

    cr.execute("""CREATE TABLE account_tax_group(
        id SERIAL NOT NULL PRIMARY KEY,
        name varchar,
        sequence int4
            )
        """)

    cr.execute("""INSERT INTO account_tax_group
        (name) VALUES ('migration')
        RETURNING id""")

    group_id = cr.fetchone()[0]

    cr.execute("""UPDATE account_tax
        SET tax_group_id = %s
        """, (group_id,))

    """
        Migrate tax on account_move_line

       check tax_code_id on aml and find a tax which has base_code_id = this number, if we find one, set the value
       on aml tax_ids. If we don't find a match, check for tax with tax_code_id = this number and if we find one,
       set the value on aml tax_line_id. except if debit=credit=0 then do nothing
    """
    util.create_column(cr, 'account_move_line', 'tax_line_id', 'int4')

    if not util.table_exists(cr, 'account_move_line_account_tax_rel'):
        util.create_m2m(cr, 'account_move_line_account_tax_rel', 'account_move_line', 'account_tax')

    # Create index for faster update
    cr.execute("""create index account_move_line_tax_line_idx on account_move_line (tax_line_id)""")
    cr.execute(
        """create index account_tax_code_ids_idx on account_tax
        (tax_code_id, base_code_id, ref_tax_code_id, ref_base_code_id)"""
    )

    # Perform several pass to increase performance
    cr.execute("""UPDATE account_move_line a
        SET tax_line_id = t.id
        FROM account_tax t
        WHERE a.name = t.name AND a.tax_code_id in (t.tax_code_id, t.ref_tax_code_id) AND
              a.tax_code_id IS NOT NULL AND (t.tax_code_id IS NOT NULL OR t.ref_tax_code_id IS NOT NULL) AND
              a.tax_amount != 0
        """)

    cr.execute("""UPDATE account_move_line a
        SET tax_line_id = t.id
        FROM account_tax t
        WHERE a.tax_code_id in (t.tax_code_id, t.ref_tax_code_id) AND
              a.tax_line_id IS NULL AND
              a.tax_code_id IS NOT NULL AND (t.tax_code_id IS NOT NULL OR t.ref_tax_code_id IS NOT NULL) AND
              a.tax_amount != 0 AND
              (a.name LIKE '%' || t.name OR a.name LIKE t.name || '%' OR
               t.name LIKE '%' || a.name OR t.name LIKE a.name || '%') AND
              char_length(a.name) / char_length(t.name) BETWEEN 0.6 AND 1.4
        """)

    cr.execute("""UPDATE account_move_line a
        SET tax_line_id = t.id
        FROM account_tax t
        WHERE a.tax_code_id in (t.tax_code_id, t.ref_tax_code_id) AND
              a.tax_code_id IS NOT NULL AND (t.tax_code_id IS NOT NULL OR t.ref_tax_code_id IS NOT NULL) AND
              a.tax_amount != 0 AND
              a.tax_line_id IS NULL AND
              (a.name LIKE '%' || t.name || '%' OR t.name LIKE '%' || a.name || '%') AND
              char_length(a.name) / char_length(t.name) BETWEEN 0.6 AND 1.4
        """)

    # Mapping between invoice_id and list of tax on those invoices
    cr.execute(
        """
        SELECT i.move_id, t.tax_id, SUBSTRING(SPLIT_PART(l.name, E'\n', 1), 0, 65) as name
          FROM account_invoice i
          JOIN account_invoice_line l on l.invoice_id = i.id
          JOIN account_invoice_line_tax t on t.invoice_line_id = l.id
        """
    )

    invoices_mapping = {}
    for invoice in cr.dictfetchall():
        if invoices_mapping.get(invoice['move_id'], False):
            invoices_mapping[invoice['move_id']].append((invoice['tax_id'], invoice['name']))
        else:
            invoices_mapping[invoice['move_id']] = [(invoice['tax_id'], invoice['name'])]

    if True:
        cr.execute("""SELECT a.id, a.debit, a.credit, a.account_id, t.id AS tax_id, t.parent_id as parent_tax_id,
                            t.name, a.move_id, a.name as aml_name
                        FROM account_move_line a, account_tax t
                        WHERE (t.base_code_id = a.tax_code_id OR t.ref_base_code_id = a.tax_code_id)
                            AND a.tax_code_id IS NOT NULL AND a.tax_amount != 0 AND t.company_id = a.company_id
                            AND (t.base_code_id IS NOT NULL OR t.ref_base_code_id IS NOT NULL)
                            AND a.tax_line_id IS NULL
                    """)
        mapped = {}
        not_mapped = {}
        invoiced_mapped = {}
        for aml in cr.dictfetchall():
            if (aml['debit'] != 0 or aml['credit'] != 0) and not mapped.get(aml['id']):
                tax_id = False
                invoice_tax_list = invoices_mapping.get(aml['move_id'], False)
                if invoice_tax_list:
                    tax_id = False
                    # Check if one of the invoice line has the same name and value as tax_id
                    # If yes, keep that one
                    if ((aml['tax_id'], aml['aml_name']) in invoice_tax_list):
                        tax_id = aml['tax_id']
                    elif ((aml['parent_tax_id'], aml['aml_name']) in invoice_tax_list):
                        tax_id = aml['parent_tax_id']
                    else:
                        taxes_id = [t[0] for t in invoice_tax_list]
                        temp_tax_id = aml['tax_id'] in taxes_id and aml['tax_id'] \
                            or aml['parent_tax_id'] in taxes_id and aml['parent_tax_id']\
                            or False
                        if temp_tax_id and not invoiced_mapped.get(aml['id'], False):
                            invoiced_mapped[aml['id']] = temp_tax_id
                if not tax_id:
                    not_mapped[aml['id']] = aml['tax_id']
                else:
                    cr.execute("""INSERT INTO account_move_line_account_tax_rel(account_move_line_id, account_tax_id)
                                    VALUES(%s, %s)
                                """, (aml['id'], tax_id))
                    mapped[aml['id']] = tax_id

        for k, v in invoiced_mapped.items():
            if not mapped.get(k, False):
                cr.execute("""INSERT INTO account_move_line_account_tax_rel(account_move_line_id, account_tax_id)
                                    VALUES(%s, %s)
                                """, (k, v))
                mapped[k] = v

        for k, v in not_mapped.items():
            if not mapped.get(k, False):
                cr.execute("""INSERT INTO account_move_line_account_tax_rel(account_move_line_id, account_tax_id)
                                    VALUES(%s, %s)
                                """, (k, v))

    cr.execute("""SELECT aml.id, aml.debit, aml.credit, aml.account_id, tax.id AS tax_id, tax.parent_id as parent_tax_id,
                     tax.name, aml.move_id, aml.name as aml_name
                    FROM account_move_line aml, account_tax tax
                    WHERE (tax.tax_code_id = aml.tax_code_id OR tax.ref_tax_code_id = aml.tax_code_id)
                        AND aml.tax_code_id IS NOT NULL AND aml.tax_amount != 0  AND tax.company_id = aml.company_id
                        AND NOT EXISTS (
                           SELECT 1
                             FROM account_tax t
                            WHERE (t.base_code_id = aml.tax_code_id OR t.ref_base_code_id = aml.tax_code_id)
                              AND t.company_id = aml.company_id)

                """)
    mapped = {}
    not_mapped = {}
    invoiced_mapped = {}
    for aml in cr.dictfetchall():
        if (aml['debit'] != 0 or aml['credit'] != 0) and not mapped.get(aml['id']):
            tax_id = False
            invoice_tax_list = invoices_mapping.get(aml['move_id'], False)
            if invoice_tax_list:
                tax_id = False
                # Check if one of the invoice line has the same name and value as tax_id
                # If yes, keep that one
                if ((aml['tax_id'], aml['aml_name']) in invoice_tax_list):
                    tax_id = aml['tax_id']
                elif ((aml['parent_tax_id'], aml['aml_name']) in invoice_tax_list):
                    tax_id = aml['parent_tax_id']
                else:
                    taxes_id = [t[0] for t in invoice_tax_list]
                    temp_tax_id = aml['tax_id'] in taxes_id and aml['tax_id'] \
                        or aml['parent_tax_id'] in taxes_id and aml['parent_tax_id']\
                        or False
                    if temp_tax_id and not invoiced_mapped.get(aml['id'], False):
                        invoiced_mapped[aml['id']] = temp_tax_id
            if not tax_id:
                not_mapped[aml['id']] = aml['tax_id']
            else:
                cr.execute("""UPDATE account_move_line SET tax_line_id = %s WHERE id = %s AND tax_line_id IS NULL
                            """, (tax_id, aml['id']))
                mapped[aml['id']] = tax_id

    for k, v in invoiced_mapped.items():
        if not mapped.get(k, False):
            cr.execute("""UPDATE account_move_line SET tax_line_id = %s WHERE id = %s AND tax_line_id IS NULL
                            """, (v, k))
            mapped[k] = v

    for k, v in not_mapped.items():
        if not mapped.get(k, False):
            cr.execute("""UPDATE account_move_line SET tax_line_id = %s WHERE id = %s AND tax_line_id IS NULL
                            """, (v, k))

    # delete index
    cr.execute("""drop index account_move_line_tax_line_idx""")
    cr.execute("""drop index account_tax_code_ids_idx""")

    cr.execute("UPDATE account_tax SET type_tax_use = 'none' WHERE parent_id IS NOT NULL")

    columns = map(','.join, util.get_columns(cr, 'account_tax', ('id', 'name', 'type_tax_use')))[0]
    cr.execute(""" INSERT INTO account_tax (name, type_tax_use, {columns})
                        SELECT name || ' (purchase)', 'purchase', {columns}
                          FROM account_tax
                         WHERE type_tax_use = 'all'
    """.format(columns=columns))

    cr.execute("""UPDATE account_tax
                     SET type_tax_use = 'sale', name = name || ' (sale)'
                   WHERE type_tax_use = 'all'
    """)
