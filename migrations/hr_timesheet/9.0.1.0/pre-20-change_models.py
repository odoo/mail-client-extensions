# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_analytic_line", "is_timesheet", "boolean")
    if not util.get_index_on(cr, "hr_analytic_timesheet", "line_id"):
        cr.execute("CREATE INDEX ON hr_analytic_timesheet(line_id)")
    cr.execute(
        """
        UPDATE account_analytic_line l
           SET is_timesheet = EXISTS(SELECT 1 FROM hr_analytic_timesheet WHERE line_id=l.id)
    """
    )

    # flabgastingly slow and useless - disabled
    # cr.execute("SELECT id, line_id FROM hr_analytic_timesheet")
    # for tid, lid in cr.fetchall():
    #    util.replace_record_references(cr,
    #                                   ('hr.analytic.timesheet', tid),
    #                                   ('account.analytic.line', lid))

    for model, res_model, res_id in util.res_model_res_id(cr):
        if (res_id and model != "ir.values") or model.startswith("ir.model"):
            continue
        table = util.table_of_model(cr, model)
        cr.execute(
            "UPDATE {0} SET {1}='account.analytic.line' WHERE {1}='hr.analytic.timesheet'".format(table, res_model)
        )

    # only on real many2one that may be changes
    if util.column_exists(cr, "base_action_rule", "model_id"):
        cr.execute(
            """
            SELECT id
              FROM ir_model
             WHERE model IN ('account.analytic.line', 'hr.analytic.timesheet')
          ORDER BY 1
        """
        )
        aal, hat = [x[0] for x in cr.fetchall()]
        cr.execute("UPDATE base_action_rule SET model_id=%s WHERE model_id=%s", [aal, hat])

    # can't delete it here - project_timesheet and project_issue_sheet both require the data
    # during migration
    # util.delete_model(cr, 'hr.analytic.timesheet')

    util.delete_model(cr, "hr.sign.out.project")
    util.delete_model(cr, "hr.sign.in.project")
