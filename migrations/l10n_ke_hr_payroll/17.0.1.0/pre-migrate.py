from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, "hr.contract", *eb("l10n_ke_vol{o,u}ntary_medical_insurance"))
