# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
import difflib

def create_sequence(cr, journal, refund):
    prefix = journal['code'].upper() + '/%(year)s/'
    if refund:
        prefix = 'R'+prefix
    cr.execute("""INSERT INTO ir_sequence(name, implementation, prefix, padding, number_increment, number_next, use_date_range, company_id)
                     VALUES (%s, 'no_gap', %s, 4, 1, 1, true, %s)
                     RETURNING id""", (journal['name'], prefix, journal['company_id']))
    return cr.fetchone()

def find_match_any(journal, already_mapped, list_journals):
    journal_type = 'sale' if journal['type'] == 'sale_refund' else 'purchase'
    company_id = journal['company_id']
    for j in list_journals:
        if j['type'] == journal_type and j['company_id'] == company_id and j['id'] not in already_mapped:
            return j['id']
    return False

def find_match(cr, journal):
    # Find an invoice with journal_id = journal and check it's origin field, if it has one
    # find the invoice referenced by name=origin and check it's journal, it should be the match
    # we are looking for.
    cr.execute("""SELECT DISTINCT(a.journal_id) 
                    FROM account_invoice a, account_invoice b, account_journal j , account_journal k
                    WHERE a.journal_id=j.id AND j.company_id=%s AND b.journal_id=%s AND a.number=b.origin AND b.journal_id=k.id
                        AND ((a.type = 'in_invoice' AND b.type = 'in_refund') OR (a.type = 'out_invoice' AND b.type = 'out_refund'))
                        AND ((j.type = 'sale' AND k.type = 'sale_refund') OR (j.type = 'purchase' AND k.type = 'purchase_refund'))
                """, (journal['company_id'], journal['id']))
    journals = cr.dictfetchall()
    if len(journals) == 1:
        return journals[0]['journal_id']
    else:
        if len(journals) == 0:
            return False
        else:
            raise util.MigrationError("Found severals(%d) matching possibilites to merge journal '%s'" % (len(journals), journal['name']))
    return False

def migrate(cr, version):
    """
        Journal of type sale_refund and purchase_refund have disappeared and are now 
        a sequence number on the sale/purchase journal
    """
    # It is possible that the column have been created during specific migration in base so this check is needed
    if not util.column_exists(cr, 'account_journal', 'refund_sequence_id'):
        util.create_column(cr, 'account_journal', 'refund_sequence_id', 'integer')
        util.create_column(cr, 'account_journal', 'refund_sequence', 'bool')

    mapping = {}
    # We need to perform a mapping between sale journal and sale_refund journal and purchase and purchase_refund
    cr.execute("""SELECT id, name, code, type, company_id, sequence_id 
                    FROM account_journal 
                    WHERE type IN ('sale_refund', 'purchase_refund') 
                    ORDER BY company_id
                """)
    journals = cr.dictfetchall()
    cr.execute("""SELECT id, name, code, type, company_id, sequence_id 
                    FROM account_journal 
                    WHERE type IN ('sale', 'purchase') 
                    ORDER BY company_id
                """)
    list_journals = cr.dictfetchall()
    unmatched = []
    for journal in journals:
        if journal['type'] in ('sale_refund', 'purchase_refund'):
            match = find_match(cr, journal)
            if not match:
                # Could not find any match using invoice refund so it means that either we never performed a refund
                # Or that we have a refund journal with no equivalent. Either way, we will try to match those case at the end.
                unmatched.append(journal)
            else:
                if mapping.get(match):
                    raise util.MigrationError("Found severals(%d) matching possibilites to merge journal '%s'" % (len(journals), journal['name']))
                mapping[match] = journal['id']
                cr.execute("""UPDATE account_journal
                            SET refund_sequence_id = %s,
                            refund_sequence = true
                            WHERE id = %s
                    """, (journal['sequence_id'], match))

    #We have found all the match we could, now post-process the refund journal for whom we could not find any match
    for journal in unmatched:
        match = find_match_any(journal, mapping.keys(), list_journals)
        if match:
            mapping[match] = journal['id']
            cr.execute("""UPDATE account_journal
                        SET refund_sequence_id = %s,
                        refund_sequence = true
                        WHERE id = %s
                """, (journal['sequence_id'], match))
        else:
            # Could not match to any other journal, meaning that we have more refund journal than other journal.
            # In this case, change type of journal to sale/purchase
            seq_id = create_sequence(cr, journal, False)
            cr.execute("""UPDATE account_journal SET type = %s,
                            refund_sequence = true,
                            sequence_id = %s,
                            refund_sequence_id = %s
                            WHERE id = %s""", 
                            ('sale' if journal['type'] == 'sale_refund' else 'purchase', seq_id, journal['sequence_id'], journal['id']))

    # Now that we have a mapping, update reference on table that might have a journal_id of type sale_refund/purchase_refund
    TABLES = ['account_move_line', 'account_move', 'account_invoice']
    for k, v in mapping.items():
        for table in TABLES:
            cr.execute("""UPDATE %s
                            SET journal_id = %s
                            WHERE journal_id = %s
                        """ % (table, k, v))

    # Drop journal of type sale_refund and purchase_refund
    cr.execute("""DELETE FROM account_journal WHERE type IN ('sale_refund', 'purchase_refund')""")

    # We also have to create a dedicated refund_sequence_id for all the sale/purchase journal that does not have one after migration
    # This is to prevent numerotation error in their invoices in case they do not use a dedicated refund_sequence
    for journal in list_journals:
        seq_id = create_sequence(cr, journal, True)
        cr.execute("""UPDATE account_journal SET 
                        refund_sequence = true,
                        refund_sequence_id = %s
                        WHERE id = %s""", 
                        (seq_id, journal['id']))

    """
        We only show on dashboard journals of type sale, purchase, cash and bank
    """
    util.create_column(cr, 'account_journal', 'show_on_dashboard', 'bool')

    cr.execute("""UPDATE account_journal
        SET show_on_dashboard = 't'
        WHERE type IN ('sale', 'purchase', 'cash', 'bank')""")
