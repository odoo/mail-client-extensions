from itertools import zip_longest

from odoo.tools import float_round

from odoo.addons.base.maintenance.migrations.account.tests.test_common import TestAccountingSetupCommon
from odoo.addons.base.maintenance.migrations.util import version_gte


class TestReportValuesCommon(TestAccountingSetupCommon, abstract=True):
    def _generate_invoices_with_taxes(self):
        """Generate:
        - an invoice and a credit note with a line for each sale tax,
        - a vendor bill and a vendor credit note with a line for each purchase tax.

        Useful when testing that a tax report is left unchanged by a migration."""

        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "lst_price": 1000.0,
                "standard_price": 800.0,
            }
        )

        def create_invoice(move_type, taxes, price_offset=0):
            invoice_lines_vals = [
                {
                    "product_id": self.product.id,
                    "quantity": 1.0,
                    "price_unit": float_round(price_offset + 1.1**i, precision_digits=2),
                    "tax_ids": [(6, 0, tax.ids)],
                }
                for i, tax in enumerate(taxes)
            ]
            move = self.env["account.move"].create(
                [
                    {
                        "move_type": move_type,
                        "invoice_date": "2023-08-10",
                        "date": "2023-08-10",
                        "partner_id": self.company.partner_id.id,
                        "invoice_line_ids": [(0, 0, invoice_line_vals) for invoice_line_vals in invoice_lines_vals],
                    }
                ]
            )
            move.action_post()
            return move

        # Create an invoice and a credit note with a different sales tax on each line.
        sale_taxes = (
            self.env["account.tax"]
            .with_context(active_test=False)
            .search([("company_id", "=", self.company.id), ("type_tax_use", "=", "sale")])
        )
        create_invoice("out_invoice", sale_taxes, price_offset=10000)
        create_invoice("out_refund", sale_taxes, price_offset=1000)

        # Create a vendor bill and a vendor credit note with a different purchase tax on each line.
        purchase_taxes = (
            self.env["account.tax"]
            .with_context(active_test=False)
            .search([("company_id", "=", self.company.id), ("type_tax_use", "=", "purchase")])
        )
        create_invoice("in_invoice", purchase_taxes, price_offset=100)
        create_invoice("in_refund", purchase_taxes, price_offset=10)

    def _prepare_report_values(self, old_report_xmlid, options):
        """Generate the old report, and retrieve its lines' values for post-mig testing.

        :param options: the report_options dict to generate the report with
        :param old_report_xmlid: the xmlid of the old (pre-migration) report"""

        report = self.env.ref(old_report_xmlid).with_company(self.company)
        options["selected_variant_id"] = report.id
        old_values = self._get_report_values(report, options)
        return [
            {
                "old_report_xmlid": old_report_xmlid,
                "options": options,
                "old_values": old_values,
            }
        ]

    def _check_report_values(self, config, report_data, new_report_xmlid=None, get_new_xmlid=None):
        """Check that the old report lines' values have not been changed by the migration.

        :param config: the test config created by TestAccountingSetupCommon._prepare
        :param report_data: returned by self._prepare_report_values
        :param new_report_xmlid: (optional) the new report's xmlid, if different from the old report's
        :param get_new_xmlid: (optional) function that, for an old line's xmlid, gives you
                              the xmlid of the corresponding new line."""

        company = self.env["res.company"].browse(config["company_id"])
        new_report_xmlid = new_report_xmlid or report_data["old_report_xmlid"]
        report = self.env.ref(new_report_xmlid).with_company(company)
        options = report_data["options"]
        options.update({"selected_variant_id": report.id})

        old_values = report_data["old_values"]
        new_values = self._get_report_values(report, options)

        if get_new_xmlid is None:
            new_module = new_report_xmlid.split(".", 1)[0]

            def get_new_xmlid(old_line_xmlid):
                old_line_xmlid = old_line_xmlid.split(".", 1)[1]
                return f"{new_module}.{old_line_xmlid}"

        self.assertReportValuesUnchanged(old_values, new_values, get_new_xmlid)

    def assertReportValuesUnchanged(self, old_values, new_values, get_new_xmlid):
        """Assert that all the old report lines are present in the new report lines,
        and that their values are the same in the new report.

        Do not bother about any lines in the new report that were not in the old report.

        :param old_values: a dict {report_line_xmlid: [line_values]} of the old report lines
        :param new_values: a dict {report_line_xmlid: [line_values]} of the new report lines
        :param get_new_xmlid: function that, for an old line's xmlid, gives you the xmlid
                              of the corresponding new line
        :raises AssertionError: if any old line is not present or has a different value in the new lines."""

        errored_lines = []
        for old_xmlid, old_line_values in old_values.items():
            new_xmlid = get_new_xmlid(old_xmlid)
            new_line_values = new_values.get(new_xmlid, [])
            if any(new_value != old_value for old_value, new_value in zip_longest(old_line_values, new_line_values)):
                errored_lines.append(str((old_xmlid, old_line_values, new_xmlid, new_line_values)))

        if errored_lines:
            msg = (
                "Some report lines are not the same before and after the migration:\n"
                "(old_xmlid, old_line_values, new_xmlid, new_line_values)\n"
            )
            msg += "\n".join(errored_lines)
            self.fail(msg)

    def _get_report_values(self, report, options):
        """Helper to generate a report and extract the values from the
        lines in order to compare them before and after a migration.

        :param report:  The report to generate
        :param options: The options dict
        :return:        dict {report_line_xmlid: [line_values]}"""

        line_xmlids = report.line_ids.get_external_id()
        options = report.get_options(options) if version_gte("saas~16.4") else report._get_options(options)
        generated_lines = report._get_lines(options)

        values = {}
        for generated_line in generated_lines:
            line_xmlid = line_xmlids[
                self.env["account.report"]._get_res_id_from_line_id(generated_line["id"], "account.report.line")
            ]
            line_values = [col["no_format"] for col in generated_line["columns"]]
            values.update({line_xmlid: line_values})

        return values
