# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests import Form
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations import util


@change_version('saas~12.4')
class TestAccountPocalypseStockAccount(UpgradeCase):

    def _prepare_test_1_single_currency(self):
        invoice_form = Form(self.env['account.invoice'].with_context(type='out_invoice'), view='account.invoice_form')
        invoice_form.partner_id = self.partner
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
            line_form.quantity = 5.0
            line_form.invoice_line_tax_ids.clear()
            line_form.invoice_line_tax_ids.add(self.tax_sale)
        invoice = invoice_form.save()
        invoice.action_invoice_open()

        product_move_lines = invoice.move_id.line_ids.filtered('product_id').sorted('balance')
        self.assertRecordValues(product_move_lines, [
            {'account_id': self.account_income.id,      'debit': 0.0,   'credit': 75.0},
            {'account_id': self.account_stock_out.id,   'debit': 0.0,   'credit': 50.0},
            {'account_id': self.account_expense.id,     'debit': 50.0,  'credit': 0.0},
        ])
        return invoice.move_id.id

    def _check_test_1_single_currency(self, config, move_id):
        invoice = self.env['account.move'].browse(move_id)

        product_move_lines = invoice.line_ids.filtered('product_id').sorted('balance')
        self.assertRecordValues(product_move_lines, [
            {'account_id': config['account_income_id'],     'debit': 0.0,   'credit': 75.0, 'is_anglo_saxon_line': False},
            {'account_id': config['account_stock_out_id'],  'debit': 0.0,   'credit': 50.0, 'is_anglo_saxon_line': True},
            {'account_id': config['account_expense_id'],    'debit': 50.0,  'credit': 0.0,  'is_anglo_saxon_line': True},
        ])

    def prepare(self):
        test_name = 'TestAccountPocalypseStockAccount'

        # When the migration is made directly from an older version than saas-12.3, this test won't work because the
        # tax configuration is completely different.
        if not util.version_gte('saas~12.3'):
            self.skipTest("%s skipped because the current version is older than saas-12.3." % test_name)

        # Create company.
        company = self.env['res.company'].create({'name': "company for %s" % test_name})

        # Create user.
        user = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'user %s' % test_name,
            'login': test_name,
            'groups_id': [(6, 0, self.env.user.groups_id.ids), (4, self.env.ref('account.group_account_user').id)],
            'company_ids': [(6, 0, company.ids)],
            'company_id': company.id,
        })
        user.partner_id.email = '%s@test.com' % test_name

        self.env = self.env(user=user)
        self.cr = self.env.cr

        chart_template = self.env.ref('l10n_generic_coa.configurable_chart_template', raise_if_not_found=False)
        if not chart_template:
            self.skipTest("%s skipped because the user's company has no chart of accounts." % test_name)

        chart_template.try_loading_for_current_company()

        # Enable anglo_saxon accounting.
        company.anglo_saxon_accounting = True

        # Setup taxes.
        self.tax_sale = self.env['account.tax'].create({
            'name': "Tax %s" % test_name,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            'amount': 15,
        })

        company.account_sale_tax_id = self.tax_sale

        # Setup accounts.
        self.account_income = self.env['account.account'].search([
            ('company_id', '=', company.id),
            ('user_type_id', '=', self.env.ref('account.data_account_type_revenue').id)
        ], limit=1)
        self.account_expense = self.env['account.account'].search([
            ('company_id', '=', company.id),
            ('user_type_id', '=', self.env.ref('account.data_account_type_expenses').id)
        ], limit=1)
        self.account_receivable = self.env['account.account'].search([
            ('company_id', '=', company.id),
            ('user_type_id.type', '=', 'receivable')
        ], limit=1)
        self.account_stock_in = self.env['account.account'].create({
            'name': 'account_stock_in',
            'code': 'STOCKIN',
            'reconcile': True,
            'user_type_id': self.env.ref('account.data_account_type_current_assets').id,
            'company_id': company.id,
        })
        self.account_stock_out = self.env['account.account'].create({
            'name': 'account_stock_out',
            'code': 'STOCKOUT',
            'reconcile': True,
            'user_type_id': self.env.ref('account.data_account_type_current_assets').id,
            'company_id': company.id,
        })

        # Setup product.
        self.stock_account_product_categ = self.env['product.category'].create({
            'name': 'Test category',
            'property_valuation': 'real_time',
            'property_cost_method': 'fifo',
            'property_stock_account_input_categ_id': self.account_stock_in.id,
            'property_stock_account_output_categ_id': self.account_stock_out.id,
        })

        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.product = self.env['product.product'].create({
            'name': "Test product %s" % test_name,
            'type': 'product',
            'categ_id': self.stock_account_product_categ.id,
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id,
            'standard_price': 10.0,
            'lst_price': 15.0,
            'property_account_income_id': self.account_income.id,
            'property_account_expense_id': self.account_expense.id,
        })

        # Setup partner.
        self.partner = self.env['res.partner'].create({
            'name': "Test partner %s" % test_name,
            'property_account_receivable_id': self.account_receivable.id,
            'company_id': company.id,
        })

        # Initial Vendor bill.
        invoice_form = Form(self.env['account.invoice'].with_context(type='in_invoice'), view='account.invoice_supplier_form')
        invoice_form.partner_id = self.partner
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
            line_form.quantity = 100.0
        invoice = invoice_form.save()
        invoice.action_invoice_open()

        return {
            'tests': [
                self._prepare_test_1_single_currency(),
            ],
            'config': {
                'tax_sale_id': self.tax_sale.id,
                'account_income_id': self.account_income.id,
                'account_expense_id': self.account_expense.id,
                'account_stock_in_id': self.account_stock_in.id,
                'account_stock_out_id': self.account_stock_out.id,
            },
        }

    def check(self, init):
        config = init['config']
        self._check_test_1_single_currency(config, init['tests'][0])
