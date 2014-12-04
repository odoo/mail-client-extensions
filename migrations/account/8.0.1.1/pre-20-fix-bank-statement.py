from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    pos = ""
    if util.column_exists(cr, 'account_bank_statement', 'pos_session_id'):
        # POS is installed, ignore bank statements linked to a pos session
        pos = "AND pos_session_id IS NULL"
    cr.execute("""UPDATE account_bank_statement_line
                     SET account_id=NULL
                   WHERE statement_id IN (SELECT id
                                            FROM account_bank_statement
                                           WHERE state='draft'
                                           {0})
               """.format(pos))
