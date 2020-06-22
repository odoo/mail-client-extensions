# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    old = util.ref(cr, "l10n_nl.tag_nl_13")
    new = util.ref(cr, "l10n_nl.tag_nl_40")
    if old and new:
        util.replace_record_references_batch(cr, {old: new}, "account.account.tag", replace_xmlid=False)
