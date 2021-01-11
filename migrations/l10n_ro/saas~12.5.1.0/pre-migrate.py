# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.replace_record_references_batch(
        cr,
        {util.ref(cr, "l10n_ro.data_account_type_not_classified"): util.ref(cr, "account.data_account_off_sheet")},
        "account.account.type",
        replace_xmlid=False,
    )
    util.remove_record(cr, "l10n_ro.data_account_type_not_classified")
