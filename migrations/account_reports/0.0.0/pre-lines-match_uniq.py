from odoo import models

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pass


if not util.version_gte("16.0"):
    from odoo.addons.account_reports.models import account_financial_report  # noqa

    class AccountFinancialHtmlReportLine(models.Model):
        _inherit = "account.financial.html.report.line"
        _module = "account_reports"
        _match_uniq = True
        _match_uniq_warning = (
            "Your existing financial report line '{xmlid}' has been merged with the standard one "
            "that has the same name '{name}'. You should check it to confirm that there is issue."
        )
