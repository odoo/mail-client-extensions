# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests import tagged, Form
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version('12.4')
class TestPurchaseStock(UpgradeCase):

    def prepare(self):
        company = self.env['res.company'].create({'name': "company for TestPurchaseStock"})

        # Create user.
        user = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'user TestPurchaseStock',
            'login': 'TestPurchaseStock',
            'groups_id': [(6, 0, self.env.user.groups_id.ids), (4, self.env.ref('account.group_account_user').id)],
            'company_ids': [(6, 0, company.ids)],
            'company_id': company.id,
        })
        user.partner_id.email = 'TestPurchaseStock@test.com'

        env_user = user.sudo(user).env

        chart_template = env_user.ref('l10n_generic_coa.configurable_chart_template', raise_if_not_found=False)
        if not chart_template:
            self.skipTest(self, "Accounting Tests skipped because the user's company has no chart of accounts.")

        chart_template.try_loading_for_current_company()

        # Enable anglo_saxon accounting.
        company.anglo_saxon_accounting = True

        # Setup accounts.
        account_expense = env_user['account.account'].search([
            ('company_id', '=', company.id),
            ('user_type_id', '=', env_user.ref('account.data_account_type_expenses').id)
        ], limit=1)
        account_payable = env_user['account.account'].search([
            ('company_id', '=', company.id),
            ('user_type_id.type', '=', 'payable')
        ], limit=1)
        account_stock_in = env_user['account.account'].create({
            'name': 'account_stock_in',
            'code': 'STOCKIN',
            'reconcile': True,
            'user_type_id': env_user.ref('account.data_account_type_current_assets').id,
            'company_id': company.id,
        })
        account_stock_out = env_user['account.account'].create({
            'name': 'account_stock_out',
            'code': 'STOCKOUT',
            'reconcile': True,
            'user_type_id': env_user.ref('account.data_account_type_current_assets').id,
            'company_id': company.id,
        })
        account_stock_valuation = env_user['account.account'].create({
            'name': 'account_stock_valuation',
            'code': 'STOCKVAL',
            'reconcile': True,
            'user_type_id': env_user.ref('account.data_account_type_current_assets').id,
            'company_id': company.id,
        })
        account_stock_price_diff = env_user['account.account'].create({
            'name': 'account_stock_price_diff',
            'code': 'STOCKPDIFF',
            'reconcile': True,
            'user_type_id': env_user.ref('account.data_account_type_current_assets').id,
            'company_id': company.id,
        })

        # Setup product.
        stock_account_product_categ = env_user['product.category'].create({
            'name': 'Test category',
            'property_valuation': 'real_time',
            'property_cost_method': 'fifo',
            'property_stock_valuation_account_id': account_stock_valuation.id,
            'property_stock_account_input_categ_id': account_stock_in.id,
            'property_stock_account_output_categ_id': account_stock_out.id,
            'property_account_creditor_price_difference_categ': account_stock_price_diff.id,
        })

        uom_unit = env_user.ref('uom.product_uom_unit')
        product = env_user['product.product'].create({
            'name': "Test product TestPurchaseStock",
            'type': 'product',
            'categ_id': stock_account_product_categ.id,
            'uom_id': uom_unit.id,
            'uom_po_id': uom_unit.id,
            'property_account_expense_id': account_expense.id,
        })

        # Setup partner.
        partner = env_user['res.partner'].create({
            'name': "Test partner TestPurchaseStock",
            'property_account_payable_id': account_payable.id,
            'company_id': company.id,
        })

        # Purchase order.
        po_form = Form(env_user['purchase.order'])
        po_form.partner_id = partner
        with po_form.order_line.new() as line:
            line.product_id = product
            line.product_qty = 1.0
            line.price_unit = 9.0
        po = po_form.save()

        po.button_approve()

        # Vendor bill.
        invoice_form = Form(env_user['account.invoice'].with_context(type='in_invoice'), view='account.invoice_supplier_form')
        invoice_form.partner_id = partner
        invoice_form.purchase_id = po
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.quantity = 1.0
            line_form.price_unit = 12.0
        invoice = invoice_form.save()
        invoice.action_invoice_open()

        #       account         |   price_unit  |   debit   |   credit  |
        # ---------------------------------------------------------------
        # stock input account   |          12.0 |       9.0 |           |   (invoice line)
        # price diff account    |               |       3.0 |           |

        product_move_lines = invoice.move_id.line_ids.filtered('product_id').sorted('balance')
        self.assertEqual(len(product_move_lines), 2)
        self.assertEqual(invoice.amount_untaxed, 12.0)
        self.assertEqual(product_move_lines[0].account_id, account_stock_price_diff)
        self.assertEqual(product_move_lines[0].balance, 3.0)
        self.assertEqual(product_move_lines[1].account_id, account_stock_in)
        self.assertEqual(product_move_lines[1].balance, 9.0)

        return {
            'move_id': invoice.move_id.id,
            'account_stock_in_id': account_stock_in.id,
            'account_stock_price_diff_id': account_stock_price_diff.id,
        }

    def check(self, init):
        move = self.env['account.move'].browse(init['move_id'])
        account_stock_in = self.env['account.account'].browse(init['account_stock_in_id'])
        account_stock_price_diff = self.env['account.account'].browse(init['account_stock_price_diff_id'])

        #       account         |   price_unit  |   debit   |   credit  |   anglo-saxon flag    |
        # ---------------------------------------------------------------------------------------
        # stock input account   |          12.0 |      12.0 |           |                     f |   (invoice line)
        # stock input account   |               |           |       3.0 |                     t |
        # price diff account    |               |       3.0 |           |                     t |

        self.assertRecordValues(move, [{'amount_untaxed': 12.0}])
        self.assertRecordValues(move.line_ids.filtered('product_id').sorted(lambda line: (line.account_id.id, line.balance)), [
            {'account_id': account_stock_in.id,         'price_unit': -3.0, 'balance': -3.0},
            {'account_id': account_stock_in.id,         'price_unit': 12.0, 'balance': 12.0},
            {'account_id': account_stock_price_diff.id, 'price_unit': 0.0,  'balance': 3.0},
        ])
