from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "l10n_co_dian_software_id", drop_column=False)
    util.remove_field(cr, "res.company", "l10n_co_dian_software_security_code", drop_column=False)
    util.remove_field(cr, "res.company", "l10n_co_dian_testing_id", drop_column=False)
