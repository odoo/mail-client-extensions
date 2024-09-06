from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "hr.payslip", "sepa_uetr", "iso20022_uetr")
