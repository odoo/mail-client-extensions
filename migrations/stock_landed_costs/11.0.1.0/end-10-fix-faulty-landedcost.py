from operator import itemgetter
from odoo.addons.base.maintenance.migrations import util
import logging
import os

_logger = logging.getLogger(__name__)
env_variable = 'ODOO_MIG_11_LANDEDCOST_ACCOUNT'
am_prefix = '[MIG:FIX LC]' # prefix to add to the created account_moves
aml_prefix = '[MIG:FIX LC]' # prefix to add to the created account_move_lines

def migrate(cr, version):
    """ Fix wrong landed cost
    How does landed cost work:
        When landed cost is applied (in v11, at least for stockable product, FIFO, automated valuation)
           1. It will add value (and remaining_value) in the stock move (sm)
           2. It will create two account move lines (aml)
               a. one aml on the valuation account 
               b. it's counterpart (normally on a different account)
    What is the issue:
        Sometimes the user selects the same account for valuation and counterparts.
        So point 1 is applied correctly
        but it creates two account move lines at 2. with a sum of 0.0$
        Issue occurs when you try to make an inventory valuation (without a date specified, I will look in the stock_moves)
        while when you specify a date, it looks in the account_move_line.
        This wrong amls creates differences.
    Why to fix it:
        Don't let the user have valuation issues and fix it.
    How to fix it:
        Check manually the configuration to check this will not occurs again.
        Explain the issue to the client with an example.
        This script will create new moves and account moves.
        The id value of the environment variable will be used as account for counterpart.
        This will affect accounting and VAT declaration.
        Don't run this without notify the client.
    """
    if has_unsolved_LC_issues(cr):
        if has_valid_env_variable(cr):
            fix_LC_issue(cr)
        else:
            _logger.warning("""Issue with landed cost, please read documention (comments the code).
            Then run the migration again with the environment variable %s properly set.""", (env_variable))

def has_unsolved_LC_issues(cr):
    cr.execute("""SELECT aml1.id
                    FROM account_move_line aml1
                        ,account_move_line aml2 
                    WHERE
                      aml1.ref ilike '%LC%'  
                      and aml1.ref = aml2.ref      
                      and aml1.name= aml2.name     
                      and aml1.balance>0           
                      and aml2.balance<0
                      and aml1.balance+aml2.balance=0
                      and aml1.account_id = aml2.account_id
                      and aml1.product_id = aml2.product_id 
                      and aml1.move_id = aml2.move_id
                    limit 1 -- better plan to know if there is at least one
                    """)
    if cr.rowcount:
        cr.execute("select am.id from account_move am where name like %s LIMIT 1 ", (am_prefix+"%",) )
        # If there is at least one issue fixed, this script has already run
        # Similar script can be applied both in migration 10->11 and 11->12
        return not cr.rowcount 
    return False

def has_valid_env_variable(cr):
    var = os.environ.get(env_variable) and int(os.environ.get(env_variable))
    if var:
        env = util.env(cr)
        account = env['account.account'].browse(var)
        account.ensure_one()
        if not account.deprecated:
            return True
    return False

def fix_LC_issue(cr):
    env = util.env(cr)
    counterpart_account_id = int(os.environ.get(env_variable))

    cr.execute("""
                SELECT aml1.id, aml2.id
                FROM account_move_line aml1
                     ,account_move_line aml2
                WHERE
                    aml1.ref ilike '%LC%'  
                    and aml1.ref = aml2.ref      
                    and aml1.name= aml2.name     
                    and aml1.balance>0           
                    and aml2.balance<0
                    and aml1.balance+aml2.balance=0
                    and aml1.account_id = aml2.account_id
                    and aml1.product_id = aml2.product_id 
                    and aml1.move_id = aml2.move_id
                """)
    for row in cr.fetchall():
        # get original records
        original_aml_valuation = env['account.move.line'].browse(row[0]) 
        original_aml_counterpart = env['account.move.line'].browse(row[1]) 
        original_am = original_aml_valuation.move_id # same account_move from both aml
        if original_aml_valuation.product_id.product_tmpl_id.categ_id.property_stock_valuation_account_id != original_aml_valuation.account_id:
            # this account is not the valuation account of the product, do nothing
            continue
       
        aml_valuation = {
            'name': aml_prefix+original_aml_valuation.name,
            'account_id': original_aml_valuation.account_id.id,
            'credit': original_aml_valuation.credit,
            'debit': original_aml_valuation.debit,
            'journal_id': original_aml_valuation.journal_id.id,
            'quantity': original_aml_valuation.quantity,
            'product_id': original_aml_valuation.product_id.id,
            'partner_id': original_aml_valuation.partner_id.id,
            'analytic_account_id': original_aml_valuation.analytic_account_id.id,
            'analytic_tag_ids': original_aml_valuation.analytic_tag_ids.ids,
            'tax_ids': original_aml_valuation.tax_ids.ids,
            'tax_line_id': original_aml_valuation.tax_line_id.id,
            'amount_currency': original_aml_valuation.amount_currency,
            'currency_id': original_aml_valuation.currency_id.id,
        }
        aml_counterpart = {
            'name': aml_prefix+original_aml_counterpart.name,
            'account_id': counterpart_account_id,
            'credit': original_aml_counterpart.credit,
            'debit': original_aml_counterpart.debit,
            'journal_id': original_aml_counterpart.journal_id.id,
            'quantity': original_aml_counterpart.quantity,
            'product_id': original_aml_counterpart.product_id.id,
            'partner_id': original_aml_counterpart.partner_id.id,
            'analytic_account_id': original_aml_counterpart.analytic_account_id.id,
            'analytic_tag_ids': original_aml_counterpart.analytic_tag_ids.ids,
            'tax_ids': original_aml_counterpart.tax_ids.ids,
            'tax_line_id': original_aml_counterpart.tax_line_id.id,
            'amount_currency': original_aml_counterpart.amount_currency,
            'currency_id': original_aml_counterpart.currency_id.id,
        }
        move = env['account.move'].create({
            'name': am_prefix+original_am.name,
            'ref': original_am.ref,
            'journal_id': original_am.journal_id.id,
            'state':'draft',
            'company_id': original_am.company_id.id,
            'line_ids' : [(0,0, aml_valuation), (0, 0, aml_counterpart)],
        })
        move.post()