# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "hr.employee", "id_card", "l10n_be_hr_contract_salary", "hr")
    util.move_field_to_module(cr, "hr.employee", "driving_license", "l10n_be_hr_contract_salary", "hr")

    util.create_column(cr, "hr_job", "sequence", "int4", default=10)
    cr.execute(
        """
        UPDATE hr_job
           SET sequence = id,
               no_of_recruitment = GREATEST(no_of_recruitment, 0)
    """
    )

    util.move_field_to_module(cr, "hr.department", "total_employee", "hr_holidays", "hr")

    util.remove_field(cr, "hr.plan.activity.type", "deadline_type")
    util.remove_field(cr, "hr.plan.activity.type", "deadline_days")
    util.remove_field(cr, "hr.plan.activity.type", "company_id")

    util.remove_field(cr, "hr.plan", "company_id")
    util.remove_field(cr, "hr.plan", "plan_type")
    util.remove_field(cr, "hr.plan", "trigger")
    util.remove_field(cr, "hr.plan", "trigger_onboarding")
    util.remove_field(cr, "hr.plan", "trigger_offboarding")
    util.remove_field(cr, "hr.plan", "trigger_other")
