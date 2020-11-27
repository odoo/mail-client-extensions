# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import no_fiscal_lock
from odoo import fields
from odoo.tests.common import Form


@change_version("14.1")
class TestTagNoInvert(UpgradeCase):
    def prepare(self):
        def register_payment(invoice):
            self.env['account.payment.register'].with_context(active_ids=invoice.ids, active_model='account.move').create({
                'payment_date': invoice.date,
            })._create_payments()

        def match_opposite(invoices):
            invoices.mapped('line_ids').filtered(lambda x: x.account_internal_type in ('receivable', 'payable')).reconcile()

        def neg_line_invoice_generator(inv_type, partner, account, date, tax):
            return self.env['account.move'].create({
                'move_type': inv_type,
                'partner_id': partner.id,
                'date': date,
                'invoice_line_ids': [
                    (0, 0, {
                        'name': 'test',
                        'quantity': -1,
                        'account_id': account.id,
                        'price_unit': 100,
                        'tax_ids': [(6, 0, tax.ids)],
                    }),

                    # Second line, so that the invoice doesn't have a negative total
                    (0, 0, {
                        'name': 'test',
                        'quantity': 1,
                        'account_id': account.id,
                        'price_unit': 200,
                    }),
                ],
            })

        def invoice_like_misc_generator(inv_type, partner, account, date, tax):
            account_type = tax.type_tax_use == 'sale' and 'receivable' or 'payable'
            reconcilable_account = self.env['account.account'].search([('company_id', '=', self.env.company.id),
                                                                       ('internal_type', '=', account_type)], limit=1)

            # We create the move in a form so that the onchanges creating the tax lines are called
            debit_positive = inv_type in ('in_invoice', 'out_refund')
            with Form(self.env['account.move'].with_context(default_move_type='entry')) as move_form:
                move_form.partner_id = partner
                move_form.date = date

                with move_form.line_ids.new() as base_line:
                    base_line.name = 'test'
                    base_line.account_id = account
                    base_line.tax_ids.add(tax)
                    base_line.debit = 100 if debit_positive else 0
                    base_line.credit = 0 if debit_positive else 100

                with move_form.line_ids.new() as counterpart_line:
                    counterpart_line.name = 'test'
                    counterpart_line.account_id = reconcilable_account
                    base_line.debit = 0 if debit_positive else 142
                    base_line.credit = 142 if debit_positive else 0

            return move_form.save()

        with no_fiscal_lock(self.env.cr):
            # Ensure the lock dates allow what we are doing
            self.env.company.fiscalyear_lock_date = None
            self.env.company.tax_lock_date = None
            self.env.company.period_lock_date = None

            # Create a tax report for a brand new country
            country = self.env['res.country'].create({
                'name': "Wakanda",
                'code': 'WA',
            })
            tax_report = self.env['account.tax.report'].create({
                'name': 'Test',
                'country_id': country.id,
            })
            self.env.company.account_tax_fiscal_country_id = country

            # Populate the tax report
            today = fields.Date.today()

            # Case 1: Invoice with a single, positive line and a payment
            self._instantiate_test_data(tax_report, 'case1', today, on_invoice_created=register_payment)
            # Case 2: Invoice containing a line with a negative quantity (and some tax on it), paid with a payment
            self._instantiate_test_data(tax_report, 'case2', today,
                                        invoice_generator=neg_line_invoice_generator,
                                        on_invoice_created=register_payment)
            # Case 3: Invoice reconciled with a credit note
            self._instantiate_test_data(tax_report, 'case3', today, on_all_invoices_created=match_opposite)
            # Case 4: Invoice and credit note with a negative line, reconciled together
            self._instantiate_test_data(tax_report, 'case4', today, on_all_invoices_created=match_opposite)
            # Case 5: Misc operations with taxes, reconciled together
            self._instantiate_test_data(tax_report, 'case5', today, on_all_invoices_created=match_opposite,
                                        invoice_generator=invoice_like_misc_generator)

            # Generate the report
            report_lines = self._get_report_lines(today)

            report_balances = {}
            for report_line in report_lines:
                report_balances[str(report_line['id'])] = report_line['columns'][0]['balance']

            return str(today), report_balances

    def _instantiate_test_data(self, tax_report, label, today, invoice_generator=None, on_invoice_created=None, on_all_invoices_created=None):
        def default_invoice_generator(inv_type, partner, account, date, tax):
            return self.env['account.move'].create({
                'move_type': inv_type,
                'partner_id': partner.id,
                'date': date,
                'invoice_line_ids': [(0, 0, {
                    'name': 'test',
                    'quantity': 1,
                    'account_id': account.id,
                    'price_unit': 100,
                    'tax_ids': [(6, 0, tax.ids)],
                })],
            })

        partner = self.env['res.partner'].create({'name': label})

        # Create invoice and refund using the tax we just made
        invoice_types = {
            'sale': ('out_invoice', 'out_refund'),
            'purchase': ('in_invoice', 'in_refund')
        }

        account_types = {
            'sale': self.env.ref('account.data_account_type_revenue').id,
            'purchase': self.env.ref('account.data_account_type_expenses').id,
        }
        for tax_exigibility in ('on_invoice', 'on_payment'):
            for type_tax_use in ('sale', 'purchase'):

                tax = self._instantiate_test_tax(tax_report, '%s-%s-%s' % (label, type_tax_use, tax_exigibility),
                                                 type_tax_use, tax_exigibility)

                invoices = self.env['account.move']
                account = self.env['account.account'].search([('company_id', '=', self.env.company.id),
                                                              ('user_type_id', '=', account_types[tax.type_tax_use])],
                                                              limit=1)
                for inv_type in invoice_types[tax.type_tax_use]:
                    invoice = (invoice_generator or default_invoice_generator)(inv_type, partner, account, today, tax)
                    invoice.action_post()
                    invoices += invoice

                    if on_invoice_created:
                        on_invoice_created(invoice)

                if on_all_invoices_created:
                    on_all_invoices_created(invoices)

    def _instantiate_test_tax(self, tax_report, label, type_tax_use, tax_exigibility):
        tax_report_line = self.env['account.tax.report.line'].create({
            'name': label,
            'report_id': tax_report.id,
            'tag_name': label,
            'sequence': len(tax_report.line_ids),
        })

        tax_template = self.env['account.tax.template'].create({
            'name': label,
            'amount': '42',
            'amount_type': 'percent',
            'type_tax_use': type_tax_use,
            'chart_template_id': self.env.company.chart_template_id.id,
            'tax_exigibility': tax_exigibility,
            'invoice_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base',
                    'plus_report_line_ids': tax_report_line.ids,
                }),

                (0, 0, {
                    'factor_percent': 25,
                    'repartition_type': 'tax',
                    'plus_report_line_ids': tax_report_line.ids,
                }),

                (0, 0, {
                    'factor_percent': 75,
                    'repartition_type': 'tax',
                    'plus_report_line_ids': tax_report_line.ids,
                }),
            ],
            'refund_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base',
                    'minus_report_line_ids': tax_report_line.ids,
                }),

                (0, 0, {
                    'factor_percent': 25,
                    'repartition_type': 'tax',
                    'minus_report_line_ids': tax_report_line.ids,
                }),

                (0, 0, {
                    'factor_percent': 75,
                    'repartition_type': 'tax',
                    # No tags on this repartition line, on purpose: this way we have an asymmetric
                    # repartition between invoice and refund and avoid shadowing effects if something is wrong
                }),
            ],
        })

        # The template needs an xmlid in order so that we can call _generate_tax
        self.env['ir.model.data'].create({
            'name': 'account_reports.14_1_migration_test_tax_report_tax_' + label,
            'module': 'account_reports',
            'res_id': tax_template.id,
            'model': 'account.tax.template',
        })
        tax_id = tax_template._generate_tax(self.env.user.company_id)['tax_template_to_tax'][tax_template.id]
        return self.env['account.tax'].browse(tax_id)

    def _get_report_lines(self, today):
        report = self.env['account.generic.tax.report']
        report_opt = report._get_options({
            'date': {
                'period_type': 'custom',
                'filter': 'custom',
                'date_to': today,
                'mode': 'range',
                'date_from': today
            }
        })
        new_context = report._set_context(report_opt)
        return report.with_context(new_context)._get_lines(report_opt)

    def check(self, init):
        today, report_balances = init

        for report_line in self._get_report_lines(today):
            self.assertEqual(report_line['columns'][0]['balance'],
                             report_balances[str(report_line['id'])],
                             "Tags reinversion modified the tax report!")
