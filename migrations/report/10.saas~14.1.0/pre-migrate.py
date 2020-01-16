# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, *util.expand_braces("{account_batch_deposit,report}.paperformat_batch_deposit"))

    util.force_noupdate(cr, "report.assets_common", False)
    util.force_noupdate(cr, "report.external_layout", False)

    for gone in {"external_layout_header", "external_layout_footer", "minimal_layout"}:
        util.remove_view(cr, "report." + gone)
