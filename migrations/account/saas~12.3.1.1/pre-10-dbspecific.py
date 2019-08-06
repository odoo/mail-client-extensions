# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def _openerp(cr, version):
    cr.execute(
        """
        DELETE FROM ir_ui_menu
        WHERE id in (5313, 5314, 5315, 5318)
    """
    )
    util.remove_record(cr, "l10n_be_reports.account_financial_html_report_menu_9")


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {"8851207e-1ff9-11e0-a147-001cc0f2115e": _openerp})
