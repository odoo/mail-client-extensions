# -*- coding: utf-8 -*-
import os
import uuid

from openerp.addons.base.maintenance.migrations import util
from openerp.release import series
from openerp.tools.parse_version import parse_version as pv

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

    keep_sheets = (pv(series) >= pv('9.saas~12') or
                   util.str2bool(os.environ.get('ODOO_MIG_9_EXPENSES_KEEP_SHEETS', 'yes')))
    keep_refs = []
    temp_name = str(uuid.uuid4())

    for dest_model, res_model, res_id in util.res_model_res_id(cr):
        if dest_model == 'ir.actions.act_window' or dest_model.startswith('ir.model'):
            continue
        table = util.table_of_model(cr, dest_model)
        if keep_sheets and dest_model in ['ir.attachment', 'mail.followers', 'mail.message']:
            keep_refs.append((table, res_model))
            # avoid linked data to be removed by `delete_model`
            cr.execute("UPDATE {0} SET {1}=%s WHERE {1}='hr.expense.expense'"
                       .format(table, res_model), [temp_name])

        if not res_id:
            cr.execute("UPDATE {0} SET {1}='hr.expense' WHERE {1}='hr.expense.expense'"
                       .format(table, res_model))
        else:
            cols = util.get_columns(cr, table, ('id', res_model, res_id))
            o_cols = ",".join("o." + c for c in cols)
            cols = ",".join(cols)
            cr.execute("""
                INSERT INTO {table} ({res_model}, {res_id}, {cols})
                SELECT 'hr.expense', l.id, {o_cols}
                  FROM {table} o, hr_expense_line l
                 WHERE o.{res_model} = 'hr.expense.expense'
                   AND o.{res_id} = l.expense_id
            """.format(**locals()))

    if keep_sheets:
        # rename column, will be used for migration to 10.0
        cr.execute("ALTER TABLE hr_expense_line RENAME COLUMN expense_id TO sheet_id")
        cr.execute("ALTER TABLE hr_expense_line DROP CONSTRAINT hr_expense_line_expense_id_fkey")
    else:
        util.remove_field(cr, 'hr.expense.line', 'expense_id')

    util.delete_model(cr, 'hr.expense.expense', drop_table=not keep_sheets)
    util.rename_model(cr, 'hr.expense.line', 'hr.expense')

    if keep_sheets:
        for table, res_model in keep_refs:
            cr.execute("UPDATE {0} SET {1}='hr.expense.expense' WHERE {1}=%s"
                       .format(table, res_model), [temp_name])

    # drop obsolete record rules - force re-creation
    util.remove_record(cr, 'hr_expense.property_rule_expense_manager')
    util.remove_record(cr, 'hr_expense.property_rule_expense_employee')
    util.remove_record(cr, 'hr_expense.hr_expense_comp_rule')
