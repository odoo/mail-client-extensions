# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    # Fields spouse_net_revenue/spouse_other_net_revenue
    # The selection for the fields spouse_fiscal_status has moved from
    # spouse_fiscal_status = fields.Selection([
    #     ('without income', 'Without Income'),
    #     ('with income', 'With Income')
    # To
    #     ('without_income', 'Without Income'),
    #     ('high_income', 'With High income'),
    #     ('low_income', 'With Low Income'),
    #     ('low_pension', 'With Low Pensions'),
    #     ('high_pension', 'With High Pensions')
    # Here are the different use cases
    # 1/ spouse_net_revenue == 0 and spouse_other_net_revenue == 0 --> without_income
    # 2/ 0 < spouse_net_revenue <= 233 --> low_income
    # 3/ spouse_net_revenue > 233 --> high_income
    # 4/ spouse_net_revenue == 0 and 0 < spouse_other_net_revenue <= 466 --> low_pension
    # 5/ spouse_net_revenue == 0 and spouse_other_net_revenue > 466 --> high_pension

    cr.execute(
        """
        UPDATE hr_employee
        SET spouse_fiscal_status =
            CASE
                WHEN
                    (spouse_net_revenue = 0
                    OR spouse_net_revenue IS NULL)
                    AND (spouse_other_net_revenue = 0
                    OR spouse_other_net_revenue IS NULL)
                    THEN 'without_income'
                WHEN
                    spouse_net_revenue != 0
                    AND spouse_net_revenue <= 233
                    THEN 'low_income'
                WHEN
                    spouse_net_revenue > 233
                    THEN 'high_income'
                WHEN
                    (spouse_net_revenue = 0
                    OR spouse_net_revenue IS NULL)
                    AND spouse_other_net_revenue != 0
                    AND spouse_other_net_revenue <= 466
                    THEN 'low_pension'
                WHEN
                    (spouse_net_revenue = 0
                    OR spouse_net_revenue IS NULL)
                    AND spouse_other_net_revenue > 466
                    THEN 'high_pension'
                ELSE 'without_income'
            END"""
    )

    # Removed fields
    removed_fields = {
        "hr.contract": ["transport_employer_cost", "ucm_insurance", "transport_mode_others"],
        "hr.employee": ["spouse_other_net_revenue", "spouse_net_revenue"],
        "res.users": ["spouse_other_net_revenue", "spouse_net_revenue"],
        "res.config.settings": ["default_holidays"],
    }
    if not util.module_installed(cr, "hr_contract_salary"):
        removed_fields["hr.contract"].extend(
            ["holidays", "wage_with_holidays", "final_yearly_costs", "monthly_yearly_costs"]
        )
        removed_fields["hr.contract.employee.report"] = ["final_yearly_costs"]

    for model, fields in removed_fields.items():
        for field in fields:
            util.remove_field(cr, model, field)

    util.create_column(cr, "hr_payroll_structure_type", "time_credit_type_id", "int4")
    util.create_column(cr, "hr_payslip_worked_days", "is_credit_time", "boolean")
    util.create_column(cr, "hr_work_entry", "is_credit_time", "boolean")

    util.delete_unused(cr, "l10n_be_hr_payroll.structure_type_employee_cp200_pfi")
