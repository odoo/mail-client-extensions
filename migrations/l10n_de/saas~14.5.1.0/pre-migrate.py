# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "l10n_de_pos_cert"):
        util.move_field_to_module(cr, "res.company", "l10n_de_widnr", "l10n_de_pos_cert", "l10n_de")
        # if the module is installed, `l10n_de_stnr` would always be filled
        # so there's no need to update it with the `l10n_de_nat_tax_nb` value
        util.move_field_to_module(cr, "res.company", "l10n_de_stnr", "l10n_de_pos_cert", "l10n_de")
        util.update_field_usage(cr, "res.company", "l10n_de_nat_tax_nb", "l10n_de_stnr")
        util.remove_field(cr, "res.company", "l10n_de_nat_tax_nb")
    else:
        util.rename_field(cr, "res.company", "l10n_de_nat_tax_nb", "l10n_de_stnr")
        util.create_column(cr, "res_company", "l10n_de_widnr", "varchar")
