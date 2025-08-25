from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    if fund := env.ref("l10n_au_hr_payroll_account.super_fund_example_super", raise_if_not_found=False):
        fund.usi = "1309011309"

    cr.execute(
        """
        INSERT INTO l10n_au_payslip_ytd_input (res_id, res_model, name, l10n_au_payslip_ytd_id)
             SELECT type.id, 'hr.payslip.input.type', type.name, ytd.id
               FROM hr_payslip_input_type type
         CROSS JOIN l10n_au_payslip_ytd ytd
               JOIN hr_salary_rule rule
                 ON ytd.rule_id = rule.id
              WHERE type.l10n_au_payment_type = 'allowance'
                AND type.l10n_au_paygw_treatment = 'special'
                AND rule.code IN ('ALW', 'ALW.TAXFREE')
        ON CONFLICT DO NOTHING;
        """
    )
