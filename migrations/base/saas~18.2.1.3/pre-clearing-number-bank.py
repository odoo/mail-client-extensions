from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "l10n_us"):
        util.move_field_to_module(cr, "res.partner.bank", "aba_routing", "l10n_us", "base")
        util.rename_field(cr, "res.partner.bank", "aba_routing", "clearing_number")
