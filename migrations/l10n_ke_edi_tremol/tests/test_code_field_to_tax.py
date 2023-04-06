# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.4")
class TestCodeFieldToTax(UpgradeCase):
    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------
    def _create_move_using_product(self, product, company, partner):
        """Create a move using the specified product

        In order for a tax for a product with a specified item code to be create, the product must
        be used in at least one account move. This function creates an account move using the
        product/company/partner provided.
        """
        self.env["account.move"].with_company(company).create(
            {
                "partner_id": partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "name": "mandatory line",
                            "price_unit": 10000,
                            "quantity": 1,
                            "account_id": company.default_cash_difference_income_account_id.id,
                            "tax_ids": [],
                        },
                    )
                ],
            }
        )

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------
    def _create_product_with_valid_item_code(self, company, partner):
        """Create a product with a code in the hsn code field that will be converted into a tax

        When the product has a hsn_code that matches an item code in the upgrade, and this product
        is used in at least one account move, a tax should be created with the appropriate
        l10n_ke.item.code in the tax's l10n_ke_item_code_id field. This new tax should created for
        every company that uses the ke chart template, and should be added to the product's customer
        taxes.
        """
        product_valid_item_code = self.env["product.product"].create(
            {
                "name": "Infinite Improbability Drive",
                "list_price": 10000,
                "type": "consu",
                "description": "Infinitely Improbable.",
                "l10n_ke_hsn_code": "0039.11.53",
                "l10n_ke_hsn_name": "Spacecraft including satellites and suborbital and spacecraft launch vehicles 88026000",
            }
        )
        self._create_move_using_product(product_valid_item_code, company, partner)
        return product_valid_item_code.id

    def _create_product_with_invalid_item_code(self, company, partner):
        """Create a product with an invalid code in the hsn code field (that will not be converted into a tax)

        A product with a hsn code that does not match a code from the l10n_ke.item.code model should
        not have a corresponding tax created.
        """
        product_invalid_item_code = self.env["product.product"].create(
            {
                "name": "Pan Galactic Gargle Blaster",
                "list_price": 10000,
                "type": "consu",
                "description": "Like having your brains smashed out by a slice of lemon wrapped round a large gold brick.",
                "l10n_ke_hsn_code": "1234.56.78",
                "l10n_ke_hsn_name": "The Best Drink in Existence.",
            }
        )
        self._create_move_using_product(product_invalid_item_code, company, partner)
        return product_invalid_item_code.id

    # -------------------------------------------------------------------------
    # CHECKS
    # -------------------------------------------------------------------------
    def _check_valid_tax_generated_for_valid_product(self, product, company_ids):
        # We specify the companies, since the taxes could have been generated for other companies
        # depending on the database
        taxes = product.taxes_id.filtered(lambda tax: tax.company_id in company_ids)
        self.assertEqual(len(taxes), len(company_ids))
        spaceship_item_code_id = self.env.ref("l10n_ke.item_code_2023_00391153").id
        self.assertRecordValues(
            taxes,
            [
                {
                    "name": "Exempt 0039.11.53",
                    "l10n_ke_item_code_id": spaceship_item_code_id,
                }
            ]
            * len(company_ids),
        )

    def _check_no_tax_generated_for_invalid_product(self, product, company_ids):
        # Companies are specified since no taxes should have been generated for these companies,
        # but there might be taxes for other companies depending on the database
        taxes = product.taxes_id.filtered(lambda tax: tax.company_id in company_ids)
        self.assertEqual(len(taxes), 0)

    # -------------------------------------------------------------------------
    # PREPARE
    # -------------------------------------------------------------------------
    def prepare(self):
        primary_company = self.env["res.company"].create({"name": "primary company for TestCodeFieldToTax"})
        secondary_company = self.env["res.company"].create({"name": "secondary company for TestCodeFieldToTax"})

        for company in (primary_company, secondary_company):
            if util.version_gte("saas~16.2"):
                self.env["account.chart.template"].try_loading("ke", company=company)
            else:
                chart_template = self.env.ref("l10n_ke.l10nke_chart_template", raise_if_not_found=False)
                chart_template.try_loading(company=company, install_demo=False)
        partner = self.env["res.partner"].create({"name": "Zaphod"})

        return {
            "company_ids": (primary_company.id, secondary_company.id),
            "product_ids": (
                self._create_product_with_valid_item_code(company, partner),
                self._create_product_with_invalid_item_code(company, partner),
            ),
        }

    def check(self, init):
        company_ids = self.env["res.company"].browse(init["company_ids"])
        valid_product, invalid_product = self.env["product.product"].browse(init["product_ids"])
        self._check_valid_tax_generated_for_valid_product(valid_product, company_ids)
        self._check_no_tax_generated_for_invalid_product(invalid_product, company_ids)
