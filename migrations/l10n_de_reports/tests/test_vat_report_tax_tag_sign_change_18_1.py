from odoo.addons.base.maintenance.migrations.account_reports.tests.test_common import TestReportValuesCommon
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~18.1")
class TestDEVatReport(TestReportValuesCommon):
    """
    Test the happy path of the l10n_de tax report and tax updates
    The goal is just to modify the appeareance of the tax report while not modifying its numbers
    The listed lines should appears positive instead of negative while not impacting all the others.
    """

    def _prepare_vat_report(self):
        line_report_that_should_be_inverted = (
            "l10n_de.tax_report_de_tag_59",
            "l10n_de.tax_report_de_tag_61",
            "l10n_de.tax_report_de_tag_62",
            "l10n_de.tax_report_de_tag_66",
            "l10n_de.tax_report_de_tag_67",
            "l10n_de.tax_report_de_tax_tag_55",
        )
        report_values = self._prepare_report_values(
            "l10n_de.tax_report",
            {
                "date": {
                    "date_from": "2023-08-01",
                    "date_to": "2023-08-31",
                    "mode": "range",
                    "filter": "custom",
                },
            },
        )
        de_report_values = report_values[0]["old_values"]
        for report_line_xml_id in line_report_that_should_be_inverted:
            de_report_values[report_line_xml_id][0] = -de_report_values[report_line_xml_id][0]

        return [{"l10n_de.tax_report": report_values}]

    def _check_vat_report(self, config, old_balances_by_report):
        for old_report_xmlid, old_balances in old_balances_by_report.items():
            self._check_report_values(config, old_balances[0], "l10n_de." + old_report_xmlid.split(".")[1])

    def prepare(self, chart_template_ref="de_skr03"):
        res = super().prepare(chart_template_ref)
        self._generate_invoices_with_taxes()
        res["tests"].append(("_check_vat_report", self._prepare_vat_report()))
        return res
