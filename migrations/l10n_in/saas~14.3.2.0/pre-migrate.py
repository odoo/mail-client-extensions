# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # ===============================================================
    # Multi-VAT tax reports (PR: 68349)
    # ===============================================================
    util.remove_field(cr, 'account.move', 'l10n_in_company_country_code')
    util.remove_view(cr, 'l10n_in.l10n_in_external_layout_background')
    util.remove_view(cr, 'l10n_in.l10n_in_external_layout_boxed')
    util.remove_view(cr, 'l10n_in.l10n_in_external_layout_clean')
    util.remove_view(cr, 'l10n_in.l10n_in_external_layout_standard')
