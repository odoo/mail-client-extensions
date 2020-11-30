# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import version_gte


@change_version("saas~14.4")
class TestTaxGroupCountry(UpgradeCase):
    def _prepare_test_load_from_model_data(self, test_country):
        """
        For groups loaded from XML data, we are using the module name to try and match them with the country linked to that
        localization.
        Use a fake country to avoid issues when ir.model.data are updated during the upgrade.
        """
        tax_group_id = self.env["account.tax.group"].create({"name": "Tax 30% test"})
        self.env["ir.model.data"].create(
            {"name": "Tax_30%_test", "model": "account.tax.group", "module": "l10n_zz", "res_id": tax_group_id.id}
        )
        return {"tax_group_id": tax_group_id.id, "country_id": test_country.id}

    def _prepare_test_find_company_from_tax(self, test_company):
        """
        In the most simple case, a tax group is only linked to taxes from the same tax fiscal country.
        In this case, we will simply get the country_id from the tax company.
        """
        tax_group_id = self.env["account.tax.group"].create({"name": "Tax 15% test"})
        tax_vals = {
            "name": "15% test",
            "type_tax_use": "sale",
            "amount_type": "percent",
            "amount": 15,
            "tax_group_id": tax_group_id.id,
            "company_id": test_company.id,
        }
        if version_gte("saas~14.3"):
            tax_vals["country_id"] = test_company.account_fiscal_country_id.id

        tax_id = self.env["account.tax"].create(tax_vals)
        return {"tax_id": tax_id.id}

    def _prepare_test_multiple_linked_taxes(self, test_company, second_test_company):
        """
        Tax groups linked to two or more taxes from different tax fiscal country will not be updated, and keep an empty country_id
        """
        tax_group_id = self.env["account.tax.group"].create({"name": "Tax 25% test"})
        first_tax_vals = {
            "name": "25% test",
            "type_tax_use": "sale",
            "amount_type": "percent",
            "amount": 25,
            "tax_group_id": tax_group_id.id,
            "company_id": test_company.id,
        }
        second_tax_vals = {
            "name": "35% test",
            "type_tax_use": "sale",
            "amount_type": "percent",
            "amount": 35,
            "tax_group_id": tax_group_id.id,
            "company_id": second_test_company.id,
        }
        if version_gte("saas~14.3"):
            first_tax_vals["country_id"] = test_company.account_fiscal_country_id.id
            second_tax_vals["country_id"] = second_test_company.account_fiscal_country_id.id

        self.env["account.tax"].create(first_tax_vals)
        self.env["account.tax"].create(second_tax_vals)
        return {"tax_group_id": tax_group_id.id}

    def _prepare_test_multiple_linked_taxes_country(self, test_company, second_test_company):
        """
        This tax group will first have its country set from the xml_id.
        Then, because there is two taxes with different countries linkes to it, it'll be removed to avoid any issues
        """
        tax_group_id = self.env["account.tax.group"].create({"name": "Tax 25% test"})
        self.env["ir.model.data"].create(
            {"name": "Tax_25%_test", "model": "account.tax.group", "module": "l10n_zz", "res_id": tax_group_id.id}
        )
        first_tax_vals = {
            "name": "25% test",
            "type_tax_use": "sale",
            "amount_type": "percent",
            "amount": 25,
            "tax_group_id": tax_group_id.id,
            "company_id": test_company.id,
        }
        second_tax_vals = {
            "name": "35% test",
            "type_tax_use": "sale",
            "amount_type": "percent",
            "amount": 35,
            "tax_group_id": tax_group_id.id,
            "company_id": second_test_company.id,
        }
        if version_gte("saas~14.3"):
            first_tax_vals["country_id"] = test_company.account_fiscal_country_id.id
            second_tax_vals["country_id"] = second_test_company.account_fiscal_country_id.id

        self.env["account.tax"].create(first_tax_vals)
        self.env["account.tax"].create(second_tax_vals)
        return {"tax_group_id": tax_group_id.id}

    def _check_test_load_from_model_data(self, values):
        tax_group_id = self.env["account.tax.group"].browse(values["tax_group_id"])
        country_id = self.env["res.country"].browse(values["country_id"])
        # As this tax group is recorded in the ir_model_data, the migration script will have used it to find that it comes from
        # l10n_be, and set its country to Belgium.
        self.assertEqual(tax_group_id.country_id, country_id)

    def _check_test_find_company_from_tax(self, values):
        tax_id = self.env["account.tax"].browse(values["tax_id"])
        # Compare the tax fiscal country of the tax's company with the country_id of the group.
        # As the migration take the first one to set the country of the group, they have to match
        group_country_id = tax_id.tax_group_id.country_id
        company_fiscal_country_id = tax_id.company_id.account_fiscal_country_id
        self.assertEqual(group_country_id, company_fiscal_country_id)

    def _check_test_multiple_linked_taxes(self, values):
        tax_group_id = self.env["account.tax.group"].browse(values["tax_group_id"])
        # Because we have multiple fiscal_country_ids related to a single group, that group will not have a country_id
        self.assertEqual(tax_group_id.country_id.id, False)

    def prepare(self):
        test_company_id = self.env["res.company"].create(
            {
                "name": "Test be company",
                "country_id": self.env.ref("base.be").id,
            }
        )
        test_country_id = self.env["res.country"].create({"name": "Test country", "code": "ZZ"})
        second_test_company_id = self.env["res.company"].create(
            {
                "name": "Test second company",
                "country_id": test_country_id.id,
            }
        )
        self.env["ir.model.data"].create(
            {"name": "zz", "model": "res.country", "module": "l10n_zz", "res_id": test_country_id.id}
        )
        # Test all the possible states of a tax group before and after the migration.
        return {
            "14.4-test-tax-groups": [
                # - tax groups coming from the XML data
                self._prepare_test_load_from_model_data(test_country_id),
                # - custom tax groups linked to a single tax
                self._prepare_test_find_company_from_tax(test_company_id),
                # - custom tax groups linked to multiple taxes
                self._prepare_test_multiple_linked_taxes(test_company_id, second_test_company_id),
                # - custom tax groups linked to multiple taxes w/ a country_id found in xml
                self._prepare_test_multiple_linked_taxes_country(test_company_id, second_test_company_id),
            ]
        }

    def check(self, init):
        self._check_test_load_from_model_data(init["14.4-test-tax-groups"][0])
        self._check_test_find_company_from_tax(init["14.4-test-tax-groups"][1])
        self._check_test_multiple_linked_taxes(init["14.4-test-tax-groups"][2])
        self._check_test_multiple_linked_taxes(init["14.4-test-tax-groups"][3])
