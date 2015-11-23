# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from openerp.tools import float_round

def create_new_reconciliation_entry(cr, values):
    cr.execute("""INSERT INTO account_partial_reconcile(debit_move_id, credit_move_id,
                        amount, amount_currency, currency_id, company_currency_id, company_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (values['debit_move_id'], values['credit_move_id'], values['amount'], values['amount_currency'],
                        values.get('currency_id', None), values['company_currency_id'], values['company_id']))

def find_pair(debit_move_lines, credit_move_lines):
    debit_move = debit_move_lines[0]
    credit_move = credit_move_lines[0]
    for el in debit_move_lines:
        if el['remaining']<debit_move['remaining']:
            debit_move = el
    for el in credit_move_lines:
        if el['remaining']<credit_move['remaining']:
            credit_move = el
    return (debit_move, credit_move)

def compute_amount_currency(cr, amount, currency_id, company_id, date):
    cr.execute("""SELECT r.rate, c.rounding FROM res_currency_rate r
                   LEFT JOIN res_currency c ON c.id = r.currency_id
                   WHERE r.currency_id = %s
                     AND r.name <= %s
                     AND (r.company_id is null
                         OR r.company_id = %s)
                ORDER BY r.company_id, r.name desc LIMIT 1""",
               (currency_id, date, company_id))
    res = cr.dictfetchone()
    return float_round(amount * res['rate'], precision_rounding=res['rounding'])

def migrate_reconciliation(cr, debit_move_lines, credit_move_lines, same_currency):
    while(True):
        #Find lowest debit move lines and credit move lines and create a reconciliation entry for the both of them
        #if we could not find any, exit loop it means we've reconciled everyhting we could
        if not len(debit_move_lines) or not len(credit_move_lines):
            return True
        debit_move, credit_move = find_pair(debit_move_lines, credit_move_lines)
        amount = min(debit_move['remaining'], credit_move['remaining'])
        debit_move_index = debit_move_lines.index(debit_move)
        credit_move_index = credit_move_lines.index(credit_move)
        #change remaining value and remove from list the move that has remaining value at 0
        debit_move_lines[debit_move_index]['remaining'] -= amount
        credit_move_lines[credit_move_index]['remaining'] -= amount

        line_info = {'debit_move_id': debit_move['id'],
                'credit_move_id': credit_move['id'],
                'amount': amount,
                'amount_currency': 0,
                # 'currency_id': 'NULL',
                'company_currency_id': debit_move['company_currency_id'],
                'company_id': debit_move['company_id']}

        if same_currency and same_currency is not None and same_currency != debit_move_lines[debit_move_index]['company_currency_id']:
            amount_currency = min(debit_move['remaining_currency'], credit_move['remaining_currency'])
            debit_move_lines[debit_move_index]['remaining_currency'] -= amount_currency
            credit_move_lines[credit_move_index]['remaining_currency'] -= amount_currency
            line_info['amount_currency'] = amount_currency
            line_info['currency_id'] = same_currency

        if same_currency is False:  # != None
            if debit_move_lines[debit_move_index]['currency_id']:
                line_info['currency_id'] = debit_move_lines[debit_move_index]['currency_id']
            else:
                line_info['currency_id'] = credit_move_lines[credit_move_index]['currency_id']
            if line_info['currency_id'] and line_info['currency_id'] != debit_move_lines[debit_move_index]['company_currency_id']:
                line_info['amount_currency'] = compute_amount_currency(cr, amount, line_info['currency_id'], debit_move_lines[debit_move_index]['company_id'], debit_move_lines[debit_move_index]['date'])
            else:
                line_info['amount_currency'] = 0

        if debit_move_lines[debit_move_index]['remaining'] == 0:
            debit_move_lines.remove(debit_move)
        if credit_move_lines[credit_move_index]['remaining'] == 0:
            credit_move_lines.remove(credit_move)

        create_new_reconciliation_entry(cr, line_info)

def migrate(cr, version):
    """
        Reconciliation model has been removed and replace by a many2many between aml

        Important note: On the new account_partial_reconcile table, we won't store the
        amount_currency reconciled between 2 move lines. The only problem by doing this
        is that on the invoice we will see all the payment in the company currency which
        might be different from what was before, but if invoice is done it is no big deal.
        If user really wants to see it the way it was, it can unreconciled the move and
        reconcile them again and at that moment the amount_currency will correctly be set.
        If we wanted to migrate the amount_currency, it would involves a lot of currency
        conversion between account_move_line and this might be a little overkill.
    """

    """
        Clean all account move lines where the currency_id = the company currency_id
    """

    cr.execute("""UPDATE account_move_line l
        SET amount_currency = 0, currency_id = NULL
        FROM (SELECT currency_id, id from res_company) c
        WHERE company_id = c.id and l.currency_id = c.currency_id
        """)

    cr.execute("""CREATE TABLE IF NOT EXISTS account_partial_reconcile(
                    id SERIAL NOT NULL PRIMARY KEY,
                    debit_move_id integer,
                    credit_move_id integer,
                    amount numeric,
                    amount_currency numeric,
                    currency_id integer,
                    company_currency_id integer,
                    company_id integer
                    )
                """)

    # What to do with reconcile object that has the flag opening_reconciliation set to True?
    # Nothing since we already deleted aml that belong to an opening/closing period
    cr.execute("""SELECT id FROM account_move_reconcile""")

    answers = cr.dictfetchall()
    for element in answers:
        cr.execute("""SELECT aml.id, aml.debit, aml.credit, aml.currency_id, aml.date,
                            abs(aml.amount_currency) AS remaining_currency, aml.company_id, abs(aml.debit - aml.credit) AS remaining, 
                            c.currency_id AS company_currency_id
                        FROM account_move_line aml, res_company c 
                        WHERE c.id = aml.company_id AND (reconcile_id = %s OR reconcile_partial_id = %s)""", (element['id'], element['id']))
        reconcile_moves = cr.dictfetchall()

        if reconcile_moves:
            debit_move_lines = []
            credit_move_lines = []
            same_currency = reconcile_moves[0]['currency_id']
            for element in reconcile_moves:
                if element['currency_id'] != same_currency:
                    same_currency = False
                if element['debit'] > 0:
                    debit_move_lines.append(element)
                else:
                    credit_move_lines.append(element)
            migrate_reconciliation(cr, debit_move_lines, credit_move_lines, same_currency)

    # After having filled the new table, execute an analyze on it to increase performance for further query
    # (lot of computed field use this table)
    cr.execute("""ANALYZE account_partial_reconcile""")

    #Rename table account.statement.operation.template to account.operation.template

    util.rename_model(cr, 'account.statement.operation.template', 'account.operation.template')
    cr.execute("""UPDATE account_operation_template
                    SET amount_type = 'percentage'
                    WHERE amount_type in ('percentage_of_total', 'percentage_of_balance')
                """)
