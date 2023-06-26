from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.employee", "l10n_hk_autopay_identifier")
    util.remove_field(cr, "hr.payslip", "hsbc_export")
    util.remove_field(cr, "hr.payslip", "hsbc_export_date")
    util.remove_field(cr, "hr.payslip", "hsbc_export_filename")
