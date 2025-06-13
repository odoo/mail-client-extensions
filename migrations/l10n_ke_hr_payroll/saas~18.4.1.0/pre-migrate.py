from odoo.upgrade import util


def migrate(cr, version):
    columns = [
        "l10n_ke_mortgage",
    ]
    move_columns = util.import_script("hr/saas~18.4.1.1/post-migrate.py").move_columns
    move_columns(cr, employee_columns=columns)
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_ke_hr_payroll.hr_contract{,_template}_view_form"))
