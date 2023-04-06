# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_usage(cr, "res.company", "l10n_ar_country_code", "country_code")
    util.remove_field(cr, "res.company", "l10n_ar_country_code")

    util.remove_view(cr, "l10n_ar.sequence_view")
    util.remove_view(cr, "l10n_ar.sequence_view_tree")
    util.remove_view(cr, "l10n_ar.view_sequence_search")
