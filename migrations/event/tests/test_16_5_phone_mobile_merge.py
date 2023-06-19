# -*- coding: utf-8 -*-

import datetime

from dateutil.relativedelta import relativedelta

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class TestPhoneMobileMerge(UpgradeCase):
    """Test removal of mobile field, merged with phone (and logged)"""

    def prepare(self):
        event = self.env["event.event"].create(
            {
                "date_begin": datetime.datetime.now() + relativedelta(days=-1),
                "date_end": datetime.datetime.now() + relativedelta(days=1),
                "name": "Test Event",
            }
        )
        registrations = self.env["event.registration"].create(
            [
                {
                    "event_id": event.id,
                    "name": "Phone only",
                    "phone": "+32456000000",
                    "state": "open",
                },
                {
                    "event_id": event.id,
                    "name": "Mobile only",
                    "mobile": "+32456000011",
                    "state": "open",
                },
                {
                    "event_id": event.id,
                    "name": "Both (same)",
                    "mobile": "+32456000022",
                    "phone": "+32456000022",
                    "state": "open",
                },
                {
                    "event_id": event.id,
                    "name": "Both (different)",  # only expected log
                    "mobile": "+32456000033",
                    "phone": "+32456000044",
                    "state": "open",
                },
                {
                    "event_id": event.id,
                    "name": "None",
                    "state": "open",
                },
            ]
        )
        return {"event_id": event.id, "registrations_ids": registrations.ids}

    def check(self, init):
        registrations = self.env["event.registration"].browse(init["registrations_ids"])

        expected_phone_all = ["+32456000000", "+32456000011", "+32456000022", "+32456000044", False]
        expected_msg_len_all = [2, 2, 2, 3, 2]  # creation message and event ticket + 1 with log
        for registration, expected_phone, expected_msg_len in zip(
            registrations, expected_phone_all, expected_msg_len_all
        ):
            with self.subTest(registration=registration):
                debug_info = "\n".join([msg.body for msg in registration.message_ids])
                self.assertEqual(registration.phone, expected_phone)
                self.assertEqual(len(registration.message_ids), expected_msg_len, f"Log error: {debug_info}")
                # both different -> log message
                if expected_msg_len == 3:
                    self.assertTrue(
                        any(
                            "Mobile number +32456000033 removed in favor of phone number" in message.body
                            for message in registration.message_ids
                        )
                    )
