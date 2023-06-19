# -*- coding: utf-8 -*-

import datetime

from dateutil.relativedelta import relativedelta

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class TestSaleStatusComputation(UpgradeCase):
    """Test computation of sale_status field on registrations"""

    def prepare(self):
        product = self.env["product.product"].create(
            {
                "name": "Event",
                "detailed_type": "event",
            }
        )
        event = self.env["event.event"].create(
            {
                "date_begin": datetime.datetime.now() + relativedelta(days=-1),
                "date_end": datetime.datetime.now() + relativedelta(days=1),
                "name": "Test Event",
            }
        )
        sale_ticket, free_ticket = self.env["event.event.ticket"].create(
            [
                {
                    "event_id": event.id,
                    "name": "Sale Ticket",
                    "product_id": product.id,
                    "price": 50.0,
                },
                {
                    "event_id": event.id,
                    "name": "Sale Ticket",
                    "product_id": product.id,
                    "price": 0,
                },
            ]
        )
        event_customer = self.env["res.partner"].create(
            {
                "email": "event_customer@test.example.com",
                "name": "Event Customer",
            }
        )
        draft_sale_order = self.env["sale.order"].create(
            {
                "partner_id": event_customer.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "event_id": event.id,
                            "event_ticket_id": free_ticket.id,
                            "product_id": free_ticket.product_id.id,
                            "product_uom_qty": 1,
                            "price_unit": 0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "event_id": event.id,
                            "event_ticket_id": sale_ticket.id,
                            "product_id": sale_ticket.product_id.id,
                            "product_uom_qty": 1,
                            "price_unit": 50,
                        },
                    ),
                ],
            }
        )
        self.env["event.registration"].create(
            [
                {
                    "event_id": event.id,
                    "event_ticket_id": free_ticket.id,
                    "name": "Free Registration",
                    "sale_order_id": draft_sale_order.id,
                    "sale_order_line_id": draft_sale_order.order_line[0].id,
                    "state": "draft",
                },
                {
                    "event_id": event.id,
                    "event_ticket_id": sale_ticket.id,
                    "name": "Sale Draft Registration",
                    "sale_order_id": draft_sale_order.id,
                    "sale_order_line_id": draft_sale_order.order_line[1].id,
                    "state": "draft",
                },
            ]
        )
        sent_sale_order = self.env["sale.order"].create(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "event_id": event.id,
                            "event_ticket_id": sale_ticket.id,
                            "product_id": sale_ticket.product_id.id,
                            "product_uom_qty": 1,
                            "price_unit": 50,
                        },
                    ),
                ],
                "partner_id": event_customer.id,
                "state": "sent",
            }
        )
        self.env["event.registration"].create(
            {
                "event_id": event.id,
                "event_ticket_id": sale_ticket.id,
                "name": "Sale Sent Registration",
                "sale_order_id": sent_sale_order.id,
                "sale_order_line_id": sent_sale_order.order_line.id,
                "state": "draft",
            }
        )
        sold_sale_order = self.env["sale.order"].create(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "event_id": event.id,
                            "event_ticket_id": sale_ticket.id,
                            "product_id": sale_ticket.product_id.id,
                            "product_uom_qty": 1,
                            "price_unit": 50,
                        },
                    ),
                ],
                "partner_id": event_customer.id,
                "state": "sale",
            }
        )
        self.env["event.registration"].create(
            {
                "event_id": event.id,
                "event_ticket_id": sale_ticket.id,
                "is_paid": True,
                "name": "Sale Sent Registration",
                "sale_order_id": sold_sale_order.id,
                "sale_order_line_id": sold_sale_order.order_line.id,
                "state": "open",
            }
        )
        regs_without_so = self.env["event.registration"].create(
            [
                {
                    "event_id": event.id,
                    "event_ticket_id": free_ticket.id,
                    "name": "Free Registration",
                    "state": "draft",
                },
                {
                    "event_id": event.id,
                    "event_ticket_id": sale_ticket.id,
                    "name": "Sale Draft Registration",
                    "state": "draft",
                },
                {
                    "event_id": event.id,
                    "event_ticket_id": sale_ticket.id,
                    "name": "Sale Open Registration",
                    "state": "open",
                },
            ]
        )
        return {
            "draft_sale_order_id": draft_sale_order.id,
            "regs_without_so_ids": regs_without_so.ids,
            "sent_sale_order_id": sent_sale_order.id,
            "sold_sale_order_id": sold_sale_order.id,
        }

    def check(self, init):
        draft_sale_order = self.env["sale.order"].browse(init["draft_sale_order_id"])
        sent_sale_order = self.env["sale.order"].browse(init["sent_sale_order_id"])
        sold_sale_order = self.env["sale.order"].browse(init["sold_sale_order_id"])
        regs_without_so = self.env["event.registration"].browse(init["regs_without_so_ids"]).sorted("id")

        # Registrations without SO
        for registration in regs_without_so:
            self.assertEqual(registration.sale_status, "free")

        # SO in a sent state
        self.assertEqual(len(sent_sale_order.order_line.registration_ids), 1)
        self.assertEqual(sent_sale_order.order_line.registration_ids.sale_status, "to_pay")

        # SO in a sold state
        self.assertEqual(len(sold_sale_order.order_line.registration_ids), 1)
        self.assertEqual(sold_sale_order.order_line.registration_ids.sale_status, "sold")

        # SO in a draft state
        draft_so_registrations = draft_sale_order.order_line.registration_ids
        self.assertEqual(len(draft_so_registrations), 2)
        expected_sale_status_all = ["free", "to_pay"]
        for registration, expected_sale_status in zip(draft_so_registrations, expected_sale_status_all):
            self.assertEqual(registration.sale_status, expected_sale_status)
