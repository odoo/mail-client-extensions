from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_be_hr_payroll_fleet.hr_contract_view_tree")
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll_fleet.hr_contract{,_template}_view_form"))
