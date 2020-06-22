# -*- coding: utf-8 -*-
from odoo.upgrade import util

import re


def migrate(cr, version):
    # ===========================================================
    # Sequence Performances (PR:53393)
    # ===========================================================
    util.create_column(cr, "account_journal", "sequence_override_regex", "varchar")
    for table in ['account_move', 'account_bank_statement']:
        util.create_column(cr, table, 'sequence_prefix', 'varchar')
        util.create_column(cr, table, 'sequence_number', 'int4')

    cr.execute("""
        SELECT journal.id,
               journal.name,
               COALESCE(prefix, '') AS prefix,
               COALESCE(suffix, '') AS suffix
          FROM account_journal journal
          JOIN ir_sequence sequence ON journal.sequence_id = sequence.id
    """)

    for res in cr.dictfetchall():
        substitute = {'year': 0, 'month': 0, 'range_year': 0, 'range_month': 0, 'y': 0, 'range_y': 0}
        try:
            res['prefix'] % substitute
            res['suffix'] % substitute
        except KeyError:
            raise util.MigrationError(
                "Only 'range_year', 'range_y', 'range_month', 'year' and 'month' are valid"
                " placeholders in prefix and suffix for ir.sequence on %s." % res['name']
            )
        if re.search(r'%\(\w+\)s', res['prefix']) and re.search(r'%\(\w+\)s', res['suffix']):
            raise util.MigrationError("Placeholders can not be in both prefix and suffix")

        if res['suffix'] and re.search(r'(\d|%\(\w+\)s)', res['suffix']):
            suffix_regex = res['suffix'].replace('%(year)s', r'(?P<year>(\d{4})?)')\
                                        .replace('%(y)s', r'(?P<year>(\d{2})?)')\
                                        .replace('%(month)s', r'(?P<month>(\d{2})?)')\
                                        .replace('%(range_year)s', r'(?P<year>(\d{4})?)')\
                                        .replace('%(range_y)s', r'(?P<year>(\d{2})?)')\
                                        .replace('%(range_month)s', r'(?P<month>(\d{2})?)')
            regex = r'^(?P<prefix1>.*?)(?P<seq>\d*)(?P<suffix>{})$'.format(suffix_regex)
            cr.execute("""
                UPDATE account_journal
                   SET sequence_override_regex = %(regex)s
                 WHERE id = %(journal_id)s;
            """, {
                'regex': regex,
                'journal_id': res['id'],
            })
            number = re.sub(r'\?P<\w+>', '?:', regex.replace(r'?P<seq>', ''))
            prefix = re.sub(r'\?P<\w+>', '', re.sub(r'(\?<seq>.*)', '(?:.*)', regex))
            for table in ['account_move', 'account_bank_statement']:
                cr.execute("""
                    UPDATE {}
                       SET sequence_prefix = (regexp_match(name, %(prefix)s))[1],
                           sequence_number = ('0' || (regexp_match(name, %(number)s))[1])::integer
                     WHERE journal_id = %(journal_id)s;
                """.format(table), {
                    'prefix': prefix,
                    'number': number,
                    'journal_id': res['id'],
                })

    for table in ['account_move', 'account_bank_statement']:
        cr.execute(r"""
            UPDATE %s
               SET sequence_prefix = (regexp_match(name, '^(.*?)(?:\d*)(?:\D*?)$'))[1],
                   sequence_number = ('0' || (regexp_match(name, '^(?:.*?)(\d*)(?:\D*?)$'))[1])::integer
             WHERE sequence_number IS NULL;
        """ % (table,))

    util.remove_field(cr, "account.journal", "sequence_id")
    util.remove_field(cr, "account.journal", "refund_sequence_id")
    util.remove_field(cr, "account.journal", "sequence_number_next")
    util.remove_field(cr, "account.journal", "refund_sequence_number_next")

    util.create_column(cr, "account_journal", "sale_activity_type_id", "int4")
    util.create_column(cr, "account_journal", "sale_activity_user_id", "int4")
    util.create_column(cr, "account_journal", "sale_activity_note", "text")

    util.create_column(cr, "account_move", "posted_before", "boolean")
    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
                UPDATE account_move
                   SET posted_before = (state = 'posted' OR name != '/')
            """,
        ),
    )

    util.rename_field(cr, "account.move", "invoice_payment_state", "payment_state")
    util.remove_field(cr, "account.move", "invoice_partner_icon")
    util.remove_field(cr, "account.move", "invoice_sequence_number_next")
    util.remove_field(cr, "account.move", "invoice_sequence_number_next_prefix")

    util.create_column(cr, "account_move_line", "matching_number", "varchar")
    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
                UPDATE account_move_line l
                   SET matching_number = f.name
                  FROM account_full_reconcile f
                 WHERE f.id = l.full_reconcile_id
                   AND l.matching_number IS NULL
            """,
            prefix="l.",
        ),
    )
    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
                UPDATE account_move_line l
                   SET matching_number = 'P'
                  FROM account_partial_reconcile p
                 WHERE (p.credit_move_id = l.id OR p.debit_move_id = l.id)
                   AND l.matching_number IS NULL
            """,
            prefix="l.",
        ),
    )

    util.create_column(cr, "res_company", "account_opening_date", "date")
    cr.execute(
        """
        UPDATE res_company c
           SET account_opening_date = m.date
          FROM account_move m
         WHERE m.id = c.account_opening_move_id
    """
    )

    util.rename_field(cr, "account.invoice.report", "invoice_payment_state", "payment_state")
