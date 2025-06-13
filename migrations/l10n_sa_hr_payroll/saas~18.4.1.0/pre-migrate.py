from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_sa_hr_payroll.hr_contract_{,template_}view_form"))
