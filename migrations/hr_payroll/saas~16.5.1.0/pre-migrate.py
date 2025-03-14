from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_contract", "schedule_pay", "varchar")
    util.create_column(cr, "hr_contract", "wage_type", "varchar")

    util.explode_execute(
        cr,
        """
            UPDATE hr_contract c
               SET
                   schedule_pay = st.default_schedule_pay,
                   wage_type = st.wage_type
              FROM hr_payroll_structure_type st
             WHERE c.structure_type_id = st.id
        """,
        table="hr_contract",
        alias="c",
    )

    util.remove_column(cr, "hr_payroll_structure", "schedule_pay")

    util.remove_field(cr, "hr.payslip", "normal_wage")
    util.move_field_to_module(cr, "hr.employee", "currency_id", "l10n_hk_hr_payroll", "hr_payroll")
    util.move_field_to_module(cr, "hr.payslip.worked_days", "is_credit_time", "l10n_be_hr_payroll", "hr_payroll")
    util.move_field_to_module(cr, "hr.work.entry", "is_credit_time", "l10n_be_hr_payroll", "hr_payroll")
