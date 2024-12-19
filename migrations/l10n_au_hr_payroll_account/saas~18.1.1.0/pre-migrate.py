from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "l10n_au_payslip_ytd", "l10n_au_income_stream_type", "varchar")
    cr.execute(
        """
        UPDATE l10n_au_payslip_ytd
           SET l10n_au_income_stream_type = e.l10n_au_income_stream_type
          FROM hr_employee e
         WHERE e.id = l10n_au_payslip_ytd.employee_id
        """
    )
