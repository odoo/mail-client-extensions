from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_ma_hr_payroll.hr_contract_{view_form_l10n_ma_payroll,template_view_form}"))
