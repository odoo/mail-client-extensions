# # -*- coding: utf-8 -*-

# from dateutil.relativedelta import relativedelta
# from freezegun import freeze_time

# from odoo import fields

# from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


# @change_version("15.3")
# class TestaleOrderSubscription(UpgradeCase):
#     def prepare(self):
#         currency_eur = self._prepare_currency("EUR")
#         currency_usd = self._prepare_currency("USD")
#         currency_zar = self._prepare_currency("ZAR")
#         currency_aud = self._prepare_currency("AUD")

#         pricelists = (
#             self.env["product.pricelist"]
#             .with_context(tracking_disable=True)
#             .create(
#                 [
#                     {
#                         "name": "First Pricelist %s" % currency_eur.name,
#                         "currency_id": currency_eur.id,
#                     },
#                     {
#                         "name": "Second Pricelist %s" % currency_usd.name,
#                         "currency_id": currency_usd.id,
#                     },
#                     {
#                         "name": "Third Pricelist %s" % currency_zar.name,
#                         "currency_id": currency_zar.id,
#                     },
#                     {
#                         "name": "Fourth Pricelist %s" % currency_aud.name,
#                         "currency_id": currency_aud.id,
#                     },
#                 ]
#             )
#         )
#         data = self._generate_subscriptions(pricelists)
#         subcription_to_upsell = data["sub_without_so"]
#         invoice_data = self._generate_invoices(subcription_to_upsell)
#         data["upsell_id"] = invoice_data["upsell_id"]
#         self.env.cr.commit()
#         return data

#     def _generate_subscriptions(self, pricelists):
#         with freeze_time("2022-04-25"):  # unneeded if we don't generate invoices
#             partner_count = 5
#             order_count = 3
#             uom_month = self.env.ref("sale_subscription.subscription_uom_month")
#             uom_year = self.env.ref("sale_subscription.subscription_uom_year")

#             all_partners = self.env["res.partner"].create(
#                 [{"name": "Jean-Luc %s" % idx, "email": "jean-luc-%s@opoo.com" % idx} for idx in range(partner_count)]
#             )

#             subscription_templates = self.env["sale.subscription.template"].create(
#                 [
#                     {
#                         "name": "TestSubscriptionTemplate 1 - monthly",
#                         "description": "Test Subscription Template 1 - monthly",
#                         "recurring_rule_type": "monthly",
#                         "recurring_interval": 1,
#                         "recurring_rule_boundary": "unlimited",
#                     },
#                     {
#                         "name": "TestSubscriptionTemplate 1 - yearly",
#                         "description": "Test Subscription Template 1 - yearly",
#                         "recurring_rule_type": "yearly",
#                         "recurring_interval": 1,
#                         "recurring_rule_boundary": "unlimited",
#                     },
#                 ]
#             )

#             product_values = []
#             uoms = [uom_month, uom_year, uom_month, uom_year, uom_month]
#             t_ids = subscription_templates.ids
#             template_ids = [t_ids[0], t_ids[1], t_ids[0], t_ids[1], t_ids[0]]
#             prices = [5, 10, 15, 20, 50, 75, 100, 120]
#             for idx in range(5):
#                 uom_id = uoms[idx]
#                 product_values.append(
#                     {
#                         "name": "Product %s" % idx,
#                         "list_price": prices[idx],
#                         "sale_ok": True,
#                         "recurring_invoice": True,
#                         "subscription_template_id": template_ids[idx],
#                         "uom_id": uom_id.id,
#                         "uom_po_id": uom_id.id,
#                     }
#                 )
#             all_products = self.env["product.template"].create(product_values)
#             factors = [2, 1, 30, 4]
#             ratio_per_pricelist = {k: v for k, v in zip(pricelists, factors)}
#             pricelist_item_values = []
#             for product in all_products:
#                 for pl in pricelists:
#                     pricelist_item_values.append(
#                         {
#                             "product_id": product.product_variant_ids.id,
#                             "applied_on": "0_product_variant",
#                             "compute_price": "fixed",
#                             "fixed_price": product.list_price * ratio_per_pricelist[pl],
#                             "pricelist_id": pl.id,
#                         }
#                     )

#             self.env["product.pricelist.item"].create(pricelist_item_values)
#             order_values = []
#             product_ids = all_products.product_variant_ids.ids
#             for idx in range(order_count):
#                 line_values = []
#                 product_id = self.env["product.product"].browse(product_ids[idx])
#                 line_values += [
#                     (
#                         0,
#                         0,
#                         {
#                             "name": product_id.name,
#                             "product_id": product_id.id,
#                             "product_uom_qty": 1,
#                             "qty_delivered": 1,
#                             "product_uom": product_id.uom_id.id,
#                             "price_unit": product_id.list_price,
#                         },
#                     ),
#                     (
#                         0,
#                         0,
#                         {
#                             "name": product_id.name,
#                             "product_id": product_id.id,
#                             "product_uom_qty": 1,
#                             "qty_delivered": 1,
#                             "product_uom": product_id.uom_id.id,
#                             "price_unit": product_id.list_price,
#                         },
#                     ),
#                 ]
#                 order_values.append(
#                     {
#                         "name": "SO %s" % idx,
#                         "partner_id": all_partners.ids[idx],
#                         "pricelist_id": pricelists.ids[idx],
#                         "order_line": line_values,
#                     }
#                 )

#             sale_orders = self.env["sale.order"].create(order_values)
#             sale_orders.action_confirm()
#             line_values = [
#                 (
#                     0,
#                     0,
#                     {
#                         "product_id": product_ids[0],
#                         "quantity": 2,
#                         "price_unit": 42,
#                         "uom_id": uom_month.id,
#                     },
#                 ),
#                 (
#                     0,
#                     0,
#                     {
#                         "product_id": product_ids[1],
#                         "quantity": 2,
#                         "price_unit": 21,
#                         "uom_id": uom_year.id,
#                     },
#                 ),
#             ]
#             sub_without_so = self.env["sale.subscription"].create(
#                 [
#                     {
#                         "name": "TestSubscription created without SO",
#                         "partner_id": all_partners.ids[4],
#                         "template_id": subscription_templates.ids[1],
#                         "recurring_invoice_line_ids": line_values,
#                     }
#                 ]
#             )
#             # Start the subscriptions in batch
#             next_stage_in_progress = self.env["sale.subscription.stage"].search(
#                 [("category", "=", "progress"), ("sequence", ">=", sub_without_so.stage_id.sequence)], limit=1
#             )
#             sub_without_so.stage_id = next_stage_in_progress
#             self._test_flush_tracking()
#             sale_orders.action_confirm()
#             self._test_flush_tracking()

#             return {
#                 "product_templates": all_products.ids,
#                 "sale_orders": sale_orders.ids,
#                 "sub_without_so": sub_without_so.id,
#             }

#     def _generate_invoices(self, sub_to_upsell_id):
#         subs_to_invoice = self.env["sale.subscription"].search([])
#         start_date = fields.Date.today()
#         with freeze_time(start_date - relativedelta(months=8)):
#             self.env["sale.subscription"]._cron_recurring_create_invoice()
#             self._test_flush_tracking()

#         with freeze_time(start_date - relativedelta(months=7)):
#             self.env["sale.subscription"]._cron_recurring_create_invoice()
#             self._test_flush_tracking()

#         with freeze_time(start_date - relativedelta(months=7)):
#             with freeze_time(start_date - relativedelta(months=7)):
#                 self.env["sale.subscription"]._cron_recurring_create_invoice()
#                 self._test_flush_tracking()
#             with freeze_time(start_date - relativedelta(months=6, days=10)):
#                 products = self.env["product.template"].search([("recurring_invoice", "=", True)])
#                 uom_month = self.env.ref("sale_subscription.subscription_uom_month")
#                 uom_year = self.env.ref("sale_subscription.subscription_uom_year")
#                 sub_to_upsell = self.env["sale.subscription"].browse(sub_to_upsell_id)
#                 product_0 = sub_to_upsell.recurring_invoice_line_ids[0].product_id
#                 product_1 = sub_to_upsell.recurring_invoice_line_ids[1].product_id
#                 # Add line for product and uom existing in the original sub
#                 wiz = self.env["sale.subscription.wizard"].create(
#                     {
#                         "subscription_id": sub_to_upsell_id,
#                         "option_lines": [
#                             (
#                                 0,
#                                 False,
#                                 {
#                                     "product_id": product_0.id,
#                                     "name": product_0.name,
#                                     "quantity": 5,
#                                     "uom_id": uom_month.id,
#                                 },
#                             ),
#                             (
#                                 0,
#                                 False,
#                                 {
#                                     "product_id": product_1.id,
#                                     "name": product_1.name,
#                                     "quantity": 15,
#                                     "uom_id": uom_year.id,
#                                 },
#                             ),
#                         ],
#                     }
#                 )
#                 upsell_so_id = wiz.create_sale_order()["res_id"]
#                 upsell_so = self.env["sale.order"].browse(upsell_so_id)
#                 # We make sure to reuse the same price_unit on the upsell SO to allow computation of parent_line_id by the upgrade
#                 # script
#                 upsell_so.order_line[0].price_unit = sub_to_upsell.recurring_invoice_line_ids[0].price_unit
#                 upsell_so.order_line[1].price_unit = sub_to_upsell.recurring_invoice_line_ids[1].price_unit
#                 # add line to quote manually, it must be taken into account in the subscription after validation
#                 product_2 = self.env["product.product"].browse(products.product_variant_ids.ids[2])
#                 # add line not related to the upsell so
#                 so_line_vals = [
#                     {
#                         "order_id": upsell_so_id,
#                         "product_id": product_2.id,
#                         "product_uom_qty": 2,
#                     },
#                 ]
#                 self.env["sale.order.line"].create(so_line_vals)
#                 # We don't confirm it to make sure it will be updated (parent_line_id)
#                 # upsell_so.action_confirm()
#                 self._test_flush_tracking()

#         with freeze_time(start_date - relativedelta(months=6)):
#             self.env["sale.subscription"]._cron_recurring_create_invoice()
#             self._test_flush_tracking()

#         with freeze_time(start_date - relativedelta(months=5)):
#             self.env["sale.subscription"]._cron_recurring_create_invoice()
#             self._test_flush_tracking()

#         with freeze_time(start_date - relativedelta(months=4)):
#             self.env["sale.subscription"]._cron_recurring_create_invoice()
#             self._test_flush_tracking()

#         with freeze_time(start_date - relativedelta(months=3)):
#             self.env["sale.subscription"]._cron_recurring_create_invoice()
#             self._test_flush_tracking()

#         with freeze_time(start_date - relativedelta(months=2)):
#             self.env["sale.subscription"]._cron_recurring_create_invoice()
#             self._test_flush_tracking()
#         with freeze_time(start_date - relativedelta(months=1)):
#             self.env["sale.subscription"]._cron_recurring_create_invoice()
#             self._test_flush_tracking()
#         with freeze_time(start_date):
#             self.env["sale.subscription"]._cron_recurring_create_invoice()
#             self._test_flush_tracking()

#         return {"subscription": subs_to_invoice.ids, "upsell_id": upsell_so.id}

#     def _test_flush_tracking(self):
#         """Force the creation of tracking values."""
#         self.env["base"].flush()
#         self.env.cr.precommit.run()
#         self.env.cr.flush()

#     def _test_create_invoices(self, automatic=True):
#         self._create_recurring_invoice(automatic=automatic)
#         self.invoice_ids.filtered(lambda inv: inv.state == "draft")._post(False)

#     def _prepare_currency(self, currency_code):
#         currency = (
#             self.env["res.currency"].with_context(active_test=False).search([("name", "=", currency_code.upper())])
#         )
#         currency.action_unarchive()
#         return currency

#     def check(self, init):
#         pt_ids = init["product_templates"]
#         self._check_product_values(pt_ids)
#         so_ids = init["sale_orders"]
#         self._check_so_values(so_ids)
#         self._check_upsell_values(init)

#     def _check_product_values(self, pt_ids):
#         pt_0 = self.env["product.template"].browse(pt_ids[0])
#         self.assertEqual(pt_0.product_pricing_ids[0].pricelist_id.name, "Public Pricelist")
#         self.assertEqual(pt_0.product_pricing_ids[1].pricelist_id.name, "First Pricelist EUR")
#         self.assertRecordValues(
#             pt_0.product_pricing_ids,
#             [
#                 {"duration": 1, "unit": "year", "price": 5},
#                 {"duration": 1, "unit": "month", "price": 5},
#             ],
#         )
#         pt_1 = self.env["product.template"].browse(pt_ids[1])
#         self.assertEqual(pt_1.product_pricing_ids[0].pricelist_id.name, "Public Pricelist")
#         self.assertEqual(pt_1.product_pricing_ids[1].pricelist_id.name, "Second Pricelist USD")
#         self.assertRecordValues(
#             pt_1.product_pricing_ids,
#             [
#                 {"duration": 1, "unit": "year", "price": 10},
#                 {"duration": 1, "unit": "year", "price": 10},
#             ],
#         )

#     def _check_so_values(self, so_ids):
#         so_0 = self.env["sale.order"].browse(so_ids[0])
#         self.assertEqual(so_0.pricelist_id.name, "First Pricelist EUR")
#         self.assertRecordValues(
#             so_0,
#             [
#                 {"origin_order_id": 29, "subscription_id": 29, "amount_untaxed": 10},
#             ],
#         )
#         sub_0 = so_0.subscription_id
#         self.assertEqual(sub_0.pricelist_id.name, "First Pricelist EUR")
#         self.assertRecordValues(
#             sub_0.order_line.pricing_id,
#             [
#                 {"unit": "month", "price": 5},
#             ],
#         )
#         so_1 = self.env["sale.order"].browse(so_ids[1])
#         self.assertEqual(so_1.pricelist_id.name, "Second Pricelist USD")
#         self.assertRecordValues(
#             so_1,
#             [
#                 {"origin_order_id": 30, "subscription_id": 30, "amount_untaxed": 20},
#             ],
#         )
#         sub_1 = so_1.subscription_id
#         self.assertEqual(sub_1.pricelist_id.name, "Second Pricelist USD")
#         self.assertRecordValues(
#             sub_1.order_line.pricing_id,
#             [
#                 {"unit": "year", "price": 10},
#             ],
#         )

#         so_2 = self.env["sale.order"].browse(so_ids[2])
#         self.assertEqual(so_2.pricelist_id.name, "Third Pricelist ZAR")
#         self.assertRecordValues(
#             so_2,
#             [
#                 {"origin_order_id": 28, "subscription_id": 28, "amount_untaxed": 30},
#             ],
#         )
#         return True

#     def _check_upsell_values(self, init):
#         upsell_id = init["upsell_id"]
#         upsell_so = self.env["sale.order"].browse(upsell_id)
#         subscription = upsell_so.subscription_id
#         pricing_0 = subscription.order_line.pricing_id[0]
#         pricing_1 = subscription.order_line.pricing_id[1]
#         self.assertRecordValues(
#             upsell_so.order_line.pricing_id,
#             [
#                 {"unit": pricing_0.unit, "price": pricing_0.price},
#                 {"unit": pricing_1.unit, "price": pricing_1.price},
#             ],
#         )
#         today = fields.Datetime.today()
#         self.assertRecordValues(
#             upsell_so.order_line,
#             [
#                 {
#                     "price_unit": 42,
#                     "start_date": today,
#                     "next_invoice_date": subscription.order_line[0].next_invoice_date,
#                     "parent_line_id": subscription.order_line[0].id,
#                 },
#                 {
#                     "price_unit": 21,
#                     "start_date": today,
#                     "next_invoice_date": subscription.order_line[1].next_invoice_date,
#                     "parent_line_id": subscription.order_line[1].id,
#                 },
#                 {"price_unit": 5, "start_date": False, "next_invoice_date": False, "parent_line_id": False},
#             ],
#         )
