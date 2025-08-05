from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_au_hr_payroll_account.l10n_au_superstream_sequence")
    util.remove_view(cr, "l10n_au_hr_payroll_account.hr_payslip_run_form_inherit_l10n_au_hr_payroll")
    util.remove_field(cr, "l10n_au.previous.payroll.transfer.employee", "import_ytd")
