# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "l10n_mx_edi_extended"):
        util.move_field_to_module(cr, "res.partner", "l10n_mx_edi_colony", "l10n_mx_edi", "l10n_mx_edi_extended")
        util.move_field_to_module(cr, "res.partner", "l10n_mx_edi_colony_code", "l10n_mx_edi", "l10n_mx_edi_extended")
        util.move_field_to_module(cr, "res.company", "l10n_mx_edi_colony", "l10n_mx_edi", "l10n_mx_edi_extended")
        util.move_field_to_module(cr, "res.company", "l10n_mx_edi_colony_code", "l10n_mx_edi", "l10n_mx_edi_extended")
    else:
        util.remove_field(cr, "res.partner", "l10n_mx_edi_colony")
        util.remove_field(cr, "res.partner", "l10n_mx_edi_colony_code")
        util.remove_field(cr, "res.company", "l10n_mx_edi_colony")
        util.remove_field(cr, "res.company", "l10n_mx_edi_colony_code")

    util.remove_view(cr, "l10n_mx_edi.mx_partner_address_form")
    util.remove_view(cr, "l10n_mx_edi.res_company_form_inherit_l10n_mx_edi")
