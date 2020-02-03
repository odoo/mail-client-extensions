# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for suffix in ["sold", "bought"]:
        rec = util.ref(cr, "l10n_es_reports.mod_347_operations_regular_%s" % suffix)
        util.force_noupdate(cr, "l10n_es_reports.mod_347_operations_regular_%s" % suffix, noupdate=False)
        cr.execute(
            "UPDATE account_financial_html_report_line SET code=%s WHERE id=%s", ["_mod_347_temp_%s" % suffix, rec]
        )
