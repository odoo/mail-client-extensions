# -*- coding: utf-8 -*-

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class TestAppointmentBookerId(UpgradeCase):
    def prepare(self):
        partner_1, partner_2, partner_3 = self.env["res.partner"].create(
            [
                {"email": "test_16_5_booker_id_p1@example.com", "name": "partner_1"},
                {"email": "test_16_5_booker_id_p2@example.com", "name": "partner_2"},
                {"name": "partner_3"},
            ]
        )
        user_1, user_2 = self.env["res.users"].create(
            [
                {"login": "test_16_5_booker_id_u1", "name": "test_16_5_booker_id_u1", "partner_id": partner_1.id},
                {"login": "test_16_5_booker_id_u2", "name": "test_16_5_booker_id_u2", "partner_id": partner_2.id},
            ]
        )
        appt = self.env["appointment.type"].create({"appointment_tz": "UTC", "name": "Appointment"})

        now = datetime.now()
        event_vals = {
            "appointment_type_id": appt.id,
            "name": "Test Event",
            "start": now + relativedelta(days=9),
            "stop": now + relativedelta(days=10),
            "user_id": user_1.id,
        }
        event_u1_1, event_u1_2, event_u1_3 = (
            self.env["calendar.event"]
            .with_user(user_1.sudo())
            .create(
                [
                    {
                        "appointment_type_id": appt.id,
                        "name": "Test Event",
                        "partner_ids": [(6, 0, (partner_1 + partner_2).ids)],
                        "start": now - relativedelta(days=10),
                        "stop": now - relativedelta(days=9),
                    },
                    {
                        "name": "Test Event No Appointment",
                        "partner_ids": [(6, 0, (partner_1 + partner_2).ids)],
                        "start": now + relativedelta(days=9),
                        "stop": now + relativedelta(days=10),
                    },
                    {"partner_ids": [(6, 0, (partner_1 + partner_2).ids)], **event_vals},
                ]
            )
        )
        event_u2_1, event_u2_2 = (
            self.env["calendar.event"]
            .with_user(user_2.sudo())
            .create(
                [
                    {"partner_ids": [(6, 0, (partner_1 + partner_3).ids)], **event_vals},
                    {"partner_ids": [(6, 0, partner_1.ids)], **event_vals},
                ]
            )
        )

        return {
            "event_ids": [event_u1_1.id, event_u1_2.id, event_u1_3.id, event_u2_1.id, event_u2_2.id],
            "partner_ids": [partner_1.id, partner_2.id, partner_3.id],
        }

    def check(self, init):
        event_u1_1, event_u1_2, event_u1_3, event_u2_1, event_u2_2 = self.env["calendar.event"].browse(
            init["event_ids"]
        )
        self.assertFalse(event_u1_1.appointment_booker_id)  # only update future events
        self.assertFalse(event_u1_2.appointment_booker_id)  # only update events linked to appointments
        self.assertEqual(event_u1_3.appointment_booker_id.id, init["partner_ids"][0])  # 1. partner linked to create_uid
        self.assertEqual(
            event_u2_1.appointment_booker_id.id, init["partner_ids"][2]
        )  # 2. partner not linked to responsible
        self.assertEqual(event_u2_2.appointment_booker_id.id, init["partner_ids"][0])  # 3. partner of the responsible
