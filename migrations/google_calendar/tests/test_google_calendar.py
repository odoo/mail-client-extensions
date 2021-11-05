# -*- coding: utf-8 -*-

from datetime import datetime

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~13.4")
class TestGoogleCalendar(UpgradeCase):
    def prepare(self):
        partners = self.env["res.partner"].create(
            [
                {"name": "Sandwich"},
                {"name": "Jambon-fromage"},
            ]
        )
        event = self.env["calendar.event"].create(
            {
                "name": "Casse graine",
                "start": datetime(2020, 2, 4, 8, 0),
                "stop": datetime(2020, 2, 10, 18, 0),
                "recurrency": True,
                "end_type": "count",
                "count": 2,
                "rrule_type": "monthly",
                "month_by": "date",
                "day": 4,
                "partner_ids": [(6, 0, partners.ids)],
            }
        )
        event.attendee_ids[0].google_internal_event_id = "mange"

        user = self.env["res.users"].create({"name": "Raoul Grosbedon", "login": "rgr"})
        partner = partners = self.env["res.partner"].create({"name": "Magritte Dulieu"})
        event_owner = self.env["calendar.event"].create(
            {
                "name": "Fiesta",
                "start": datetime(2020, 2, 4, 8, 0),
                "stop": datetime(2020, 2, 10, 18, 0),
                "user_id": user.id,
                "partner_ids": [(6, 0, user.partner_id.ids + partner.ids)],
            }
        )
        owner_attendee = event_owner.attendee_ids.filtered(lambda a: a.partner_id == user.partner_id)
        owner_attendee.google_internal_event_id = "danser"
        (event_owner.attendee_ids - owner_attendee).google_internal_event_id = "chanter"
        return event.id, event_owner.id

    def check(self, event_ids):
        event, event_owner = self.env["calendar.event"].browse(event_ids)

        recurrence = event.recurrence_id
        events = recurrence.calendar_event_ids.sorted("start")
        self.assertEqual(events[0].google_id, "mange_20200204T080000Z")
        self.assertEqual(events[1].google_id, "mange_20200304T080000Z")
        self.assertEqual(recurrence.google_id, "mange")

        self.assertEqual(event_owner.google_id, "danser")
