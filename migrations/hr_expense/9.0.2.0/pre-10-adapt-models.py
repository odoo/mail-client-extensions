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
               description=concat_ws('\n\n---\n\n', e.note, l.description),
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

    util.drop_workflow(cr, 'hr.expense.expense')

    for dest_model, res_model, res_id in util.res_model_res_id(cr):
        if dest_model == 'ir.actions.act_window' or dest_model.startswith('ir.model'):
            continue
        table = util.table_of_model(cr, dest_model)
        if not res_id:
            cr.execute("UPDATE {0} SET {1}='hr.expense' WHERE {1}='hr.expense.expense'"
                       .format(table, res_model))
        else:
            cols, o_cols = map(', '.join, util.get_columns(cr, table,
                                                           ('id', res_model, res_id), ['o']))
            cr.execute("""
                INSERT INTO {table} ({res_model}, {res_id}, {cols})
                SELECT 'hr.expense', l.id, {o_cols}
                  FROM {table} o, hr_expense_line l
                 WHERE o.{res_model} = 'hr.expense.expense'
                   AND o.{res_id} = l.expense_id
            """.format(**locals()))

    util.remove_column(cr, 'hr_expense_line', 'expense_id')

    # drop obsolete record rules - force re-creation
    util.remove_record(cr, 'hr_expense.property_rule_expense_manager')
    util.remove_record(cr, 'hr_expense.property_rule_expense_employee')
    util.remove_record(cr, 'hr_expense.hr_expense_comp_rule')

    util.delete_model(cr, 'hr.expense.expense')
    util.rename_model(cr, 'hr.expense.line', 'hr.expense')
