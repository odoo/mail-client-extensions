from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "report.l10n_sa_hr_payroll.master")

    util.create_column(cr, "hr_departure_reason", "l10n_sa_reason_type", "varchar")
    cr.execute("""
        UPDATE hr_departure_reason
           SET l10n_sa_reason_type = CASE
                WHEN reason_code = 9661 THEN 'clause_77'
                WHEN reason_code = 9662 THEN 'end_of_contract'
                WHEN reason_code = 342 THEN 'fired'
                WHEN reason_code = 343 THEN 'resigned'
                WHEN reason_code = 340 THEN 'retired'
                ELSE 'resigned' END
    """)
