# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.create_column(cr, "hr_contract_salary_advantage", "active", "boolean", default=True)
    util.create_column(cr, "hr_contract_salary_advantage", "activity_type_id", "int4")
    util.create_column(cr, "hr_contract_salary_advantage", "activity_creation", "varchar", default="countersigned")
    util.create_column(cr, "hr_contract_salary_advantage", "activity_creation_type", "varchar", default="always")
    util.create_column(cr, "hr_contract_salary_advantage", "activity_responsible_id", "int4")

    util.create_column(cr, "generate_simulation_link", "contract_start_date", "date")

    util.create_column(cr, "hr_contract_salary_resume", "active", "boolean", default=True)
    # The contract_type selection values only have sense in Belgium (PFI, CDI, CDD),
    # that's why we have decided to create a Many2one to hr_contract_type (new model).
    # We will move the current values of contract_type into contract_type_id in
    # l10n_be_hr_contract_salary module migration (if installed) and the column will be
    # deleted in the post-migrate of l10n_be_hr_contract_salary.
    util.create_column(cr, "hr_contract", "contract_type_id", "int4")
    util.remove_field(
        cr, "hr.contract", "contract_type", drop_column=not util.modules_installed(cr, "l10n_be_hr_contract_salary")
    )
