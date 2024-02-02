# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.company", "l10n_fr_closing_sequence_id", "l10n_fr_account", "l10n_fr")
    util.move_field_to_module(cr, "res.company", "siret", "l10n_fr_account", "l10n_fr")
    util.move_field_to_module(cr, "res.company", "ape", "l10n_fr_account", "l10n_fr")

    util.move_field_to_module(cr, "res.partner", "siret", "l10n_fr_account", "l10n_fr")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_fr{_account,}.res_company_form_l10n_fr"))
    util.rename_xmlid(cr, *eb("l10n_fr{_account,}.res_partner_form_l10n_fr"))

    util.rename_xmlid(cr, *eb("l10n_fr{_account,}.partner_demo_company_fr"))
    util.rename_xmlid(cr, *eb("l10n_fr{_account,}.demo_company_fr"))
    util.rename_xmlid(cr, *eb("l10n_fr{_account,}.demo_bank_fr"))
