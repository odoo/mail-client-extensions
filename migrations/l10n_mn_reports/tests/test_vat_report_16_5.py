import re

from odoo.addons.base.maintenance.migrations.account_reports.tests.test_common import TestReportValuesCommon
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("16.5")
class TestMNVatReport(TestReportValuesCommon):
    """Test the migration of the VAT report to the tax tags engine."""

    def _prepare_vat_report(self):
        old_report_xmlid = "l10n_mn_reports.account_report_vat_report"
        options = {
            "date": {
                "date_from": "2023-08-01",
                "date_to": "2023-08-31",
                "mode": "range",
                "filter": "custom",
            },
        }
        return self._prepare_report_values(old_report_xmlid, options)

    def _check_vat_report(self, config, report_data):
        new_report_xmlid = "l10n_mn.account_report_vat_report"

        old_line_xmlid_regex = re.compile(r"^l10n_mn_reports.vat_report_line([1-9]\d?)([a-d]?)$")

        def get_new_xmlid(old_xmlid):
            match = old_line_xmlid_regex.match(old_xmlid)
            if match:
                number, letter = int(match.group(1)), match.group(2)
                if 1 <= number <= 10 and not letter:
                    return f"l10n_mn.vat_report_line{number}"
                elif 12 <= number <= 37 and not letter:
                    return f"l10n_mn.vat_report_line{number-1}"
                elif number == 37 and letter:
                    return f"l10n_mn.vat_report_line{37 + ['a', 'b', 'c', 'd'].index(letter)}"
                elif 38 <= number <= 42 and not letter:
                    return f"l10n_mn.vat_report_line{number+3}"
                elif 44 <= number <= 63 and not letter:
                    return f"l10n_mn.vat_report_line{number+2}"

        self._check_report_values(config, report_data, new_report_xmlid, get_new_xmlid)

    def prepare(self, chart_template_ref="mn"):
        res = super().prepare(chart_template_ref)

        # We don't generate a misc entry with all the account tags because the old VAT report
        # didn't support them well.
        self._generate_invoices_with_taxes()

        res["tests"].append(("_check_vat_report", self._prepare_vat_report()))
        return res
