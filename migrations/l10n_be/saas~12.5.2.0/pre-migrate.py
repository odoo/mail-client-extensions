# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_be.attn_VAT-IN-V61")
    util.remove_record(cr, "l10n_be.attn_VAT-IN-V62")

    util.delete_unused(
        cr,
        "res_country_state",
        ["l10n_be.state_be_%s" % state for state in "van wbr bru wht wlg vli wlx wna vov vbr vwv".split()],
    )
