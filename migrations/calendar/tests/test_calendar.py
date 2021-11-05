# -*- coding: utf-8 -*-

from datetime import datetime

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~13.4")
class TestCalendarRecurrence(UpgradeCase):
    def prepare(self):
        alarms = self.env["calendar.alarm"].create(
            [
                {
                    "name": "Alarm",
                    "alarm_type": "email",
                    "interval": "minutes",
                    "duration": 20,
                },
                {
                    "name": "Alarm",
                    "alarm_type": "email",
                    "interval": "minutes",
                    "duration": 30,
                },
            ]
        )
        categories = self.env["calendar.event.type"].create([{"name": "Peter"}, {"name": "Pan"}])
        partners = self.env["res.partner"].create(
            [
                {"name": "Jean"},
                {"name": "Valjean"},
            ]
        )
        event = self.env["calendar.event"].create(
            {
                "name": "RDV avec Fée Clochette",
                "start": datetime(2020, 2, 4, 8, 0),
                "stop": datetime(2020, 2, 5, 18, 0),
                "recurrency": True,
                "end_type": "count",
                "count": 3,
                "rrule_type": "weekly",
                "tu": True,
                "partner_ids": [(6, 0, partners.ids)],
                "alarm_ids": [(6, 0, alarms.ids)],
                "categ_ids": [(6, 0, categories.ids)],
            }
        )
        return {"event": event.id, "alarms": alarms.ids, "categories": categories.ids, "partners": partners.ids}

    def check(self, init):
        event = self.env["calendar.event"].browse(init["event"])
        alarms = self.env["calendar.alarm"].browse(init["alarms"])
        categories = self.env["calendar.event.type"].browse(init["categories"])
        partners = self.env["res.partner"].browse(init["partners"])
        recurrence = event.recurrence_id
        self.assertTrue(recurrence)
        self.assertTrue(recurrence.tu)
        events = recurrence.calendar_event_ids.sorted("start")
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0].start, datetime(2020, 2, 4, 8, 0))
        self.assertEqual(events[1].start, datetime(2020, 2, 11, 8, 0))
        self.assertEqual(events[2].start, datetime(2020, 2, 18, 8, 0))
        # x2many are copied
        self.assertTrue(all(e.alarm_ids == alarms for e in events))
        self.assertTrue(all(e.categ_ids == categories for e in events))
        self.assertTrue(all(e.partner_ids == partners for e in events))
        self.assertTrue(all(e.attendee_ids.partner_id == partners for e in events))
        self.assertTrue(all(e.message_follower_ids.partner_id == partners | self.env.user.partner_id for e in events))
