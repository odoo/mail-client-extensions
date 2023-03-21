# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # l10n_mx cfid 3.0 and 4.0 merge
    util.remove_record(cr, "l10n_mx_edi.cfdiv33")
    util.remove_record(cr, "l10n_mx_edi.payment10")
    util.change_field_selection_values(cr, "account.move", "l10n_mx_edi_usage", {"P01": "S01"})
    util.remove_view(cr, "l10n_mx_edi.account_move_form_inherit_l10n_mx_edi")
    util.remove_view(cr, "l10n_mx_edi.l10n_mx_edi_inh_40_res_partner_form")
