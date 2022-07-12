# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # create missing indexes
    index_query = "CREATE INDEX {0}_{1}_index ON {0}({1})".format
    cr.execute(index_query('resource_calendar_leaves', 'holiday_id'))
    cr.execute(index_query('hr_leave', 'parent_id'))
    cr.execute(index_query('hr_leave_allocation', 'parent_id'))
    if util.column_exists(cr, 'account_analytic_line', 'holiday_id'):
        cr.execute(index_query('account_analytic_line', 'holiday_id'))

    columns = (
        set(util.get_columns(cr, 'hr_leave_allocation', ignore=('id', 'parent_id')))
        & set(util.get_columns(cr, 'hr_leave'))
    )

    util.create_column(cr, 'hr_leave_allocation', '_tmp', 'int4')
    util.remove_constraint(cr, "hr_leave_allocation", "hr_leave_allocation_type_value")
    cr.execute("""
        INSERT INTO hr_leave_allocation(_tmp, {0})
             SELECT id, {0}
               FROM hr_leave
              WHERE type='add'
    """.format(', '.join(columns)))
    cr.execute("""
        UPDATE hr_leave_allocation a
           SET parent_id = p.id
          FROM hr_leave l,
               hr_leave_allocation p
         WHERE l.id = a._tmp
           AND p._tmp = l.parent_id
    """)

    cr.execute("DELETE FROM hr_leave WHERE type='add'")
    util.remove_field(cr, 'hr.leave', 'type')
    util.remove_column(cr, 'hr_leave_allocation', '_tmp')

    util.env(cr)['hr.leave.allocation']._add_sql_constraints()
    util.env(cr)['hr.leave']._add_sql_constraints()

    # TODO create followers for allocation message.type
