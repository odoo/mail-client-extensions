# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.replace_record_references_batch(
        cr,
        {util.ref(cr, "l10n_cn.user_type_all"): util.ref(cr, "account.data_account_off_sheet")},
        "account.account.type",
        replace_xmlid=False,
    )
    util.remove_record(cr, "l10n_cn.user_type_all")
