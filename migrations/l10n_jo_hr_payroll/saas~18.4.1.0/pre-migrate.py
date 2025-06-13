from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_jo_hr_payroll.hr_contract{,_template}_view_form"))
