# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "project_project", "name", "varchar")
    util.create_column(cr, "project_project", "partner_id", "int4")
    util.create_column(cr, "project_project", "company_id", "int4")

    cr.execute("""
        UPDATE project_project p
           SET name = a.name,
               partner_id = a.partner_id,
               company_id = a.company_id
          FROM account_analytic_account a
         WHERE a.id = p.analytic_account_id
    """)

    util.remove_field(cr, "project.project", "task_needaction_count")
    # odoo/odoo@3dd3e2648329995ddc309081787e19005d48ccd0
    # This commit removes the inheritS between account.analytic.account and project.project
    # There should not be any column with an inherits, so only remove the records from `ir_model_fields`
    inherited_fields = [
        "code", "line_ids", "balance", "credit", "debit", "uom_company_id", "project_ids", "project_count",
    ]
    if util.module_installed(cr, "sale_subscription"):
        inherited_fields += ["subscription_count", "subscription_ids"]
    if util.module_installed(cr, "hr_timesheet"):
        inherited_fields += ["company_uom_id"]
    if util.module_installed(cr, "account_budget"):
        inherited_fields += ["crossovered_budget_line"]
    for fname in inherited_fields:
        util.remove_field(cr, "project.project", fname, drop_column=False)

    util.remove_record(cr, 'project.group_time_work_estimation')
    util.remove_view(cr, 'project.analytic_account_inherited_form')

    if not util.module_installed(cr, "hr_timesheet"):
        hrt = util.import_script("hr_timesheet/saas~11.3.1.0/pre-migrate.py")
        # before removing fields, we need to keep column `analytic_account_id` for later when
        # module `hr_timesheet` will be installed; but we need to remove the `ir.model.fields` in
        # the meantime.
        cr.execute("ALTER TABLE project_project RENAME COLUMN analytic_account_id TO _aa")
        for model, fields in hrt.PROJECT_FIELDS.items():
            for field in fields:
                util.remove_field(cr, model, field)
        cr.execute("ALTER TABLE project_project RENAME COLUMN _aa TO analytic_account_id")

        for x in hrt.PROJECT_XMLIDS:
            util.remove_record(cr, "project." + x)
