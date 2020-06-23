# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.version_gte("saas~13.2"):
        return

    non_forwarded_modules = """
        hr_holidays_calendar

        # enterprise
        hr_holidays_gantt_calendar
        l10n_ar_edi
        l10n_lu_reports_electronic
    """
    for module in util.splitlines(non_forwarded_modules):
        if util.module_installed(cr, module):
            raise util.MigrationError(
                "Some installed standard modules haven't been forward-ported to version `saas~13.1`. "
                "Please upgrade to a more recent version."
            )
        util.remove_module(cr, module)
