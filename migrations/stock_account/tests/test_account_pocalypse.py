# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from freezegun import freeze_time

from odoo.tests import Form

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~12.4")
class TestAccountPocalypseStockAccount(UpgradeCase):
    def _prepare_test_1_single_currency(self):
        invoice_form = Form(self.env["account.invoice"].with_context(type="out_invoice"), view="account.invoice_form")
        invoice_form.partner_id = self.partner
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_auto_fifo
            line_form.quantity = 5.0
            line_form.invoice_line_tax_ids.clear()
            line_form.invoice_line_tax_ids.add(self.tax_sale)
        invoice = invoice_form.save()
        invoice.action_invoice_open()

        product_move_lines = invoice.move_id.line_ids.filtered("product_id").sorted("balance")
        self.assertRecordValues(
            product_move_lines,
            [
                {"account_id": self.account_income.id, "debit": 0.0, "credit": 75.0},
                {"account_id": self.account_stock_out.id, "debit": 0.0, "credit": 50.0},
                {"account_id": self.account_expense.id, "debit": 50.0, "credit": 0.0},
            ],
        )
        return invoice.move_id.id

    def _check_test_1_single_currency(self, config, move_id):
        invoice = self.env["account.move"].browse(move_id)

        product_move_lines = invoice.line_ids.filtered("product_id").sorted("balance")
        self.assertRecordValues(
            product_move_lines,
            [
                {"account_id": config["account_income_id"], "debit": 0.0, "credit": 75.0, "is_anglo_saxon_line": False},
                {
                    "account_id": config["account_stock_out_id"],
                    "debit": 0.0,
                    "credit": 50.0,
                    "is_anglo_saxon_line": True,
                },
                {"account_id": config["account_expense_id"], "debit": 50.0, "credit": 0.0, "is_anglo_saxon_line": True},
            ],
        )

    def _prepare_test_fifo_vacuum(self):
        result = []
        for product in [self.product_auto_average, self.product_auto_fifo]:
            picking_form = Form(self.env["stock.picking"])
            picking_form.picking_type_id = self.env["stock.picking.type"].search([("code", "=", "outgoing")], limit=1)
            with picking_form.move_ids_without_package.new() as line_form:
                line_form.product_id = product
                line_form.product_uom_qty = 5.0
            picking = picking_form.save()
            picking.action_confirm()
            picking.move_ids_without_package.quantity_done = 5.0
            picking.button_validate()
            self.assertEquals(product.qty_available, -5.0)
            result.append((product.id, product.standard_price, product.qty_available))
        return result

    def _check_test_fifo_vacuum(self, config, values):
        self.env = self.env(user=self.env["res.users"].browse(config["user"]))
        for product_id, standard_price, qty_available in values:
            product = self.env["product.product"].browse(product_id)
            self.assertEquals(product.qty_available, qty_available)
            inventory_form = Form(self.env["stock.inventory"])
            inventory_form.name = "Inventory test_fifo_vacuum check"
            inventory_form.product_ids.clear()
            inventory_form.product_ids.add(product)
            inventory = inventory_form.save()
            inventory.action_start()
            inventory.line_ids.product_qty = 20.0
            inventory.action_validate()
            self.assertEquals(product.qty_available, 20.0)
            self.assertEquals(product.standard_price, standard_price)
            self.assertEquals(product.value_svl / product.quantity_svl, standard_price)

    def _prepare_test_price_history(self):
        with freeze_time("2020-02-01"):
            picking_form = Form(self.env["stock.picking"])
            picking_form.picking_type_id = self.env["stock.picking.type"].search([("code", "=", "incoming")], limit=1)
            with picking_form.move_ids_without_package.new() as line_form:
                line_form.product_id = self.product_auto_average_price_histo
                line_form.product_uom_qty = 5.0
            picking = picking_form.save()
            picking.move_lines.price_unit = 100
            picking.action_confirm()
            picking.move_ids_without_package.quantity_done = 5.0
            picking.button_validate()
        self.assertEquals(self.product_auto_average_price_histo.standard_price, 100)
        with freeze_time("2020-02-02"):
            self.product_auto_average_price_histo.do_change_standard_price(200, self.account_expense.id)
            self.product_auto_average_price_histo.do_change_standard_price(250, self.account_expense.id)
            self.product_auto_average_price_histo.do_change_standard_price(200, self.account_expense.id)

        with freeze_time("2020-02-03"):
            picking = picking.copy()
            picking.move_lines.price_unit = 300
            picking.action_confirm()
            picking.move_ids_without_package.quantity_done = 5.0
            picking.button_validate()

        self.assertEquals(self.product_auto_average_price_histo.standard_price, 250)
        return [
            self.product_auto_average_price_histo.id,
            self.product_auto_average_price_histo.qty_available,
            self.product_auto_average_price_histo.standard_price,
            self.env["account.move.line"].search([("product_id", "=", self.product_auto_average_price_histo.id)]).ids,
        ]

    def _check_test_price_history(self, config, values):
        self.env = self.env(user=self.env["res.users"].browse(config["user"]))
        product_auto_average_price_histo = self.env["product.product"].browse(values[0])
        svl = self.env["stock.valuation.layer"].search([("product_id", "=", product_auto_average_price_histo.id)])
        # 5.0 incoming with value of 100/unit   500
        # new cost to 200 per units             500
        # new cost to 250 per units             250
        # new cost to 200 per units             -250
        # 5.0 incoming with value of 300/unit   1500
        #
        # 10 units 2500 -> 250 per unit as standart price
        self.assertRecordValues(
            svl,
            [
                {"quantity": 5.0, "value": 500.0},
                {"quantity": 0.0, "value": 500.0},
                {"quantity": 0.0, "value": 250.0},
                {"quantity": 0.0, "value": -250.0},
                {"quantity": 5.0, "value": 1500.0},
            ],
        )
        _, qty_available, standard_price, aml_ids = values
        current_aml = self.env["account.move.line"].search([("product_id", "=", product_auto_average_price_histo.id)])
        # Ensure no change on functional fields
        self.assertEqual(qty_available, 10.0)
        self.assertEqual(standard_price, 250.0)
        self.assertEqual(sorted(current_aml.ids), sorted(aml_ids))

    def prepare(self):
        test_name = "TestAccountPocalypseStockAccount"

        # When the migration is made directly from an older version than saas-12.3, this test won't work because the
        # tax configuration is completely different.
        if not util.version_gte("saas~12.3"):
            self.skipTest("%s skipped because the current version is older than saas-12.3." % test_name)

        # Create company.
        company = self.env["res.company"].create({"name": "company for %s" % test_name})

        # Create user.
        user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "user %s" % test_name,
                    "login": test_name,
                    "groups_id": [
                        (6, 0, self.env.user.groups_id.ids),
                        (4, self.env.ref("account.group_account_user").id),
                    ],
                    "company_ids": [(6, 0, company.ids)],
                    "company_id": company.id,
                }
            )
        )
        user.partner_id.email = "%s@test.com" % test_name

        self.env = self.env(user=user)
        self.cr = self.env.cr

        chart_template = self.env.ref("l10n_generic_coa.configurable_chart_template", raise_if_not_found=False)
        if not chart_template:
            self.skipTest("%s skipped because the user's company has no chart of accounts." % test_name)

        chart_template.try_loading_for_current_company()

        # Enable anglo_saxon accounting.
        company.anglo_saxon_accounting = True

        # Setup taxes.
        self.tax_sale = self.env["account.tax"].create(
            {
                "name": "Tax %s" % test_name,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "amount": 15,
            }
        )

        company.account_sale_tax_id = self.tax_sale

        # Setup accounts.
        self.account_income = self.env["account.account"].search(
            [
                ("company_id", "=", company.id),
                ("user_type_id", "=", self.env.ref("account.data_account_type_revenue").id),
            ],
            limit=1,
        )
        self.account_expense = self.env["account.account"].search(
            [
                ("company_id", "=", company.id),
                ("user_type_id", "=", self.env.ref("account.data_account_type_expenses").id),
            ],
            limit=1,
        )
        self.account_receivable = self.env["account.account"].search(
            [("company_id", "=", company.id), ("user_type_id.type", "=", "receivable")], limit=1
        )
        self.account_stock_in = self.env["account.account"].create(
            {
                "name": "account_stock_in",
                "code": "STOCKIN",
                "reconcile": True,
                "user_type_id": self.env.ref("account.data_account_type_current_assets").id,
                "company_id": company.id,
            }
        )
        self.account_stock_out = self.env["account.account"].create(
            {
                "name": "account_stock_out",
                "code": "STOCKOUT",
                "reconcile": True,
                "user_type_id": self.env.ref("account.data_account_type_current_assets").id,
                "company_id": company.id,
            }
        )

        # Setup product.
        self.stock_account_product_categ_auto_fifo = self.env["product.category"].create(
            {
                "name": "Test category auto FIFO",
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
                "property_stock_account_input_categ_id": self.account_stock_in.id,
                "property_stock_account_output_categ_id": self.account_stock_out.id,
            }
        )

        self.stock_account_product_categ_auto_average = self.env["product.category"].create(
            {
                "name": "Test category auto average",
                "property_valuation": "real_time",
                "property_cost_method": "average",
                "property_stock_account_input_categ_id": self.account_stock_in.id,
                "property_stock_account_output_categ_id": self.account_stock_out.id,
            }
        )

        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.product_auto_fifo = self.env["product.product"].create(
            {
                "name": "Test product auto FIFO %s" % test_name,
                "type": "product",
                "categ_id": self.stock_account_product_categ_auto_fifo.id,
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
                "standard_price": 10.0,
                "lst_price": 15.0,
                "property_account_income_id": self.account_income.id,
                "property_account_expense_id": self.account_expense.id,
            }
        )
        self.product_auto_average = self.env["product.product"].create(
            {
                "name": "Test product auto average %s" % test_name,
                "type": "product",
                "categ_id": self.stock_account_product_categ_auto_average.id,
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
                "standard_price": 10.0,
                "lst_price": 15.0,
                "property_account_income_id": self.account_income.id,
                "property_account_expense_id": self.account_expense.id,
            }
        )
        with freeze_time("2020-01-01"):
            self.product_auto_average_price_histo = self.product_auto_average.copy(
                {
                    "name": "Test product auto average price history %s" % test_name,
                }
            )

        # Setup partner.
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test partner %s" % test_name,
                "property_account_receivable_id": self.account_receivable.id,
                "company_id": company.id,
            }
        )

        # Initial Vendor bill.
        invoice_form = Form(
            self.env["account.invoice"].with_context(type="in_invoice"), view="account.invoice_supplier_form"
        )
        invoice_form.partner_id = self.partner
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_auto_fifo
            line_form.quantity = 100.0
        invoice = invoice_form.save()
        invoice.action_invoice_open()

        return {
            "tests": [
                self._prepare_test_1_single_currency(),
                self._prepare_test_fifo_vacuum(),
                self._prepare_test_price_history(),
            ],
            "config": {
                "user": user.id,
                "tax_sale_id": self.tax_sale.id,
                "account_income_id": self.account_income.id,
                "account_expense_id": self.account_expense.id,
                "account_stock_in_id": self.account_stock_in.id,
                "account_stock_out_id": self.account_stock_out.id,
            },
        }

    def check(self, init):
        config = init["config"]
        self._check_test_1_single_currency(config, init["tests"][0])
        self._check_test_fifo_vacuum(config, init["tests"][1])
        self._check_test_price_history(config, init["tests"][2])
