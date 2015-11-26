# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    product = util.env(cr)['product.product'].with_context(active_test=False).search(
        [('default_code', '=', 'GEN_ODOO9_MIG')]
    )
    product_id = product.id or None

    util.rename_field(cr, 'product.template', 'hr_expense_ok', 'can_be_expensed')

    util.rename_field(cr, 'hr.expense.line', 'date_value', 'date')
    util.rename_field(cr, 'hr.expense.line', 'analytic_account', 'analytic_account_id')
    util.rename_field(cr, 'hr.expense.line', 'uom_id', 'product_uom_id')
    util.rename_field(cr, 'hr.expense.line', 'unit_quantity', 'quantity')

    for f in 'employee_id department_id journal_id company_id account_move_id currency_id'.split():
        util.create_column(cr, 'hr_expense_line', f, 'int4')

    util.create_column(cr, 'hr_expense_line', 'state', 'varchar')
    util.create_column(cr, 'hr_expense_line', 'payment_mode', 'varchar')
    util.create_column(cr, 'hr_expense_line', 'message_last_post', 'timestamp without time zone')

    cr.execute("""
        UPDATE hr_expense_line l
           SET name=concat(e.name, ': ', l.name),
               payment_mode='own_account',
               employee_id=e.employee_id,
               department_id=e.department_id,
               journal_id=e.journal_id,
               company_id=e.company_id,
               currency_id=e.currency_id,
               account_move_id=e.account_move_id,
               message_last_post=e.message_last_post,
               product_id=coalesce(product_id, %s),
               state=CASE WHEN e.state='confirm' THEN 'submit'
                          WHEN e.state='accepted' THEN 'approve'
                          WHEN e.state='done' THEN 'post'
                          WHEN e.state='paid' THEN 'done'
                          WHEN e.state='cancelled' THEN 'cancel'
                          ELSE e.state
                      END
          FROM hr_expense_expense e
         WHERE e.id = l.expense_id
    """, [product_id])

    cr.execute("""
        INSERT INTO mail_followers (res_model, res_id, partner_id)
        SELECT 'hr.expense.line', l.id, f.partner_id
          FROM mail_followers f, hr_expense_line l
         WHERE f.res_model = 'hr.expense.expense'
           AND f.res_id = l.expense_id
    """)

    cols, m_cols = map(', '.join, util.get_columns(cr, 'mail_message',
                                                   ('id', 'model', 'res_id'), ['m']))

    cr.execute("""
        INSERT INTO mail_message (model, res_id, {cols})
        SELECT 'hr.expense.line', l.id, {m_cols}
          FROM mail_message m, hr_expense_line l
         WHERE m.model = 'hr.expense.expense'
           AND m.res_id = l.expense_id
    """.format(cols=cols, m_cols=m_cols))

    util.drop_workflow(cr, 'hr.expense.expense')

    cr.execute("""UPDATE mail_message_subtype
                     SET res_model='hr.expense'
                   WHERE res_model='hr.expense.expense'
               """)

    util.remove_column(cr, 'hr_expense_line', 'expense_id')
    util.delete_model(cr, 'hr.expense.expense')
    util.rename_model(cr, 'hr.expense.line', 'hr.expense')
