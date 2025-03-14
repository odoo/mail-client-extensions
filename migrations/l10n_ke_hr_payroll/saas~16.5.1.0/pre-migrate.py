from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.contract", "l10n_ke_mortgage_interest")
    util.remove_field(cr, "hr.contract", "l10n_ke_insurance_relief")
