from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_ae_hr_payroll.hr_contract_view_form")
