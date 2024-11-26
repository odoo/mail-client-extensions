from psycopg2.extras import Json

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
          UPDATE ir_sequence
             SET company_id = NULL
           WHERE id = %s
        """,
        [util.ref(cr, "l10n_in_hr_payroll.seq_payment_advice")],
    )

    regular_pay_structure = util.ref(cr, "l10n_in_hr_payroll.hr_payroll_structure_in_employee_salary")
    worker_pay_structure = util.ref(cr, "l10n_in_hr_payroll.structure_worker_0001")
    regular_pay_structure_type = util.ref(cr, "l10n_in_hr_payroll.hr_payroll_salary_structure_type_ind_emp_pay")
    worker_pay_structure_type = util.ref(cr, "l10n_in_hr_payroll.hr_payroll_salary_structure_type_ind_worker")

    mapping = {
        regular_pay_structure: regular_pay_structure_type,
        worker_pay_structure: worker_pay_structure_type,
    }
    cr.execute(
        """
        UPDATE hr_contract
           SET structure_type_id = (%s::jsonb->hc.structure_type_id::text)::int
          FROM hr_contract hc
          JOIN res_company rc
            ON hc.company_id = rc.id
          JOIN res_partner rp
            ON rc.partner_id = rp.id
          JOIN res_country re
            ON rp.country_id = re.id
          JOIN hr_payroll_structure_type st
            ON st.id = hc.structure_type_id
         WHERE hr_contract.id = hc.id
           AND re.code = 'IN'
           AND st.default_struct_id IN %s
        """,
        [Json(mapping), tuple(mapping)],
    )

    cr.execute(
        "UPDATE ir_act_report_xml SET paperformat_id = NULL WHERE id = %s",
        [util.ref(cr, "l10n_in_hr_payroll.payslip_details_report")],
    )
    util.delete_unused(cr, "l10n_in_hr_payroll.paperformat_india_payslip")
    util.delete_unused(cr, "l10n_in_hr_payroll.l10n_in_hr_salary_rule_pfe")
