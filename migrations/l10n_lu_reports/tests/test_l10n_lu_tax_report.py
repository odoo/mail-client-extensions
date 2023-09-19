# -*- coding: utf-8 -*-
try:
    from odoo import Command
except ImportError:
    # `Command` is only available in recent versions
    Command = fields = None

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class CheckL10nLUTaxReport(UpgradeCase):
    def prepare(self):
        country_id = self.env.ref("base.lu").id
        company_ids = self.env["res.company"].create(
            [
                {"country_id": country_id, "name": "Tardis"},
                {"country_id": country_id, "name": "Tom Baker"},
            ]
        )
        tax_unit = self.env["account.tax.unit"].create(
            {
                "name": "United Federation of Planets",
                "country_id": country_id,
                "vat": "LU12345613",
                "company_ids": [Command.set(company_ids.ids)],
                "main_company_id": company_ids[0].id,
            }
        )
        report_id = self.env["l10n_lu.yearly.tax.report.manual"].create(
            {
                "company_ids": company_ids.ids,
                "avg_nb_employees_with_salary": 35,
                "phone_number": "123456789",
                "submitted_rcs": True,
                "report_section_254": 42,
                "report_section_255": 271.82,
                "year": "2022",
            }
        )

        self.env["l10n_lu_reports.report.appendix.expenditures"].create(
            {
                "report_id": report_id.id,
                "report_section_411": "Holistic Detective Agency",
                "report_section_412": 31.42,
                "report_section_413": 25.42,
            }
        )
        return {"tax_unit_id": tax_unit.id}

    def check(self, init):
        tax_unit_id = init["tax_unit_id"]
        main_company_id = self.env["account.tax.unit"].browse(tax_unit_id).main_company_id.id

        expected_vals = [
            {"ref": "l10n_lu_reports.l10n_lu_annual_tax_report_sections_108", "value": 35, "label": "balance"},
            {"ref": "l10n_lu_reports.l10n_lu_annual_tax_report_sections_237", "value": "123456789", "label": "balance"},
            {
                "ref": "l10n_lu_reports.l10n_lu_annual_tax_report_section_appendix_a_253",
                "value": 42,
                "label": "percent",
            },
            {
                "ref": "l10n_lu_reports.l10n_lu_annual_tax_report_section_appendix_a_253",
                "value": 271.82,
                "label": "vat_excluded",
            },
            {"ref": "l10n_lu_reports.l10n_lu_annual_tax_report_appendix_fg_998", "value": 1.0, "label": "balance"},
        ]

        appendix_id = self.env["l10n_lu_reports.report.appendix.expenditures"].search(
            [
                ("year", "=", "2022"),
                ("company_id", "=", main_company_id),
            ]
        )
        self.assertEqual(len(appendix_id.ids), 1)
        self.assertRecordValues(
            appendix_id,
            [
                {
                    "report_section_411": "Holistic Detective Agency",
                    "report_section_412": 31.42,
                    "report_section_413": 25.42,
                }
            ],
        )

        for vals in expected_vals:
            target_line = self.env.ref(vals["ref"])
            external_value = self.env["account.report.external.value"].search(
                [
                    ("target_report_line_id", "=", target_line.id),
                    ("target_report_expression_label", "=", vals["label"]),
                    ("company_id", "=", main_company_id),
                    ("date", "=", "2022-12-31"),
                ]
            )
            self.assertTrue(external_value.value == vals["value"] or external_value.text_value == vals["value"])

        report = self.env.ref("l10n_lu_reports.l10n_lu_annual_tax_report_section_appendix_opex")
        previous_options = {
            "date": {
                "date_from": "2022-01-01",
                "date_to": "2022-12-31",
            }
        }
        options = report.with_company(main_company_id).get_options(previous_options)
        options["export_mode"] = "print"
        report_lines = report.with_company(main_company_id)._get_lines(options)
        for column in report_lines[0]["columns"]:
            if column["expression_label"] == "vat_excluded":
                self.assertEqual(column["no_format"], 31.42)
            else:
                self.assertEqual(column["no_format"], 25.42)
