from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_payslip", "l10n_mx_edi_cfdi_state", "varchar")
    util.create_column(cr, "hr_payslip", "l10n_mx_edi_cfdi_sat_state", "varchar")
    util.create_column(cr, "hr_payslip", "l10n_mx_edi_cfdi_attachment_id", "int4")
    util.create_column(cr, "hr_payslip", "l10n_mx_edi_cfdi_uuid", "varchar")
