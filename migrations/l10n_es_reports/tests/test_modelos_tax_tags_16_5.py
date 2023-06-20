from odoo.addons.base.maintenance.migrations.account_reports.tests.test_common import TestReportValuesCommon
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~16.5")
class TestESVatReport(TestReportValuesCommon):
    """Test the migration of the l10n_es VAT reports to the tax tags engine."""

    def _prepare_vat_report(self):
        report_xmlids = ["l10n_es_reports.mod_111", "l10n_es_reports.mod_115", "l10n_es_reports.mod_303"]
        options = {
            "date": {
                "date_from": "2023-08-01",
                "date_to": "2023-08-31",
                "mode": "range",
                "filter": "custom",
            },
        }
        old_balances_by_report = {
            old_report_xmlid: self._prepare_report_values(old_report_xmlid, options)
            for old_report_xmlid in report_xmlids
        }
        return [old_balances_by_report]

    def _check_vat_report(self, config, old_balances_by_report):
        for old_report_xmlid, old_balances in old_balances_by_report.items():
            self._check_report_values(config, old_balances[0], "l10n_es." + old_report_xmlid.split(".")[1])

    def prepare(self, chart_template_ref="es_pymes"):
        res = super().prepare(chart_template_ref)

        self._generate_invoices_with_taxes()

        res["tests"].append(("_check_vat_report", self._prepare_vat_report()))
        return res
