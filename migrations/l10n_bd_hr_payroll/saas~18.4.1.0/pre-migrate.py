from odoo.upgrade import util


def migrate(cr, version):
    columns = [
        "l10n_bd_disabled_dependent",
        "l10n_bd_gazetted_war_founded_freedom_fighter",
    ]
    move_columns = util.import_script("l10n_au_hr_payroll/saas~18.4.1.0/pre-migrate.py").move_columns
    move_columns(cr, employee_columns=columns)
