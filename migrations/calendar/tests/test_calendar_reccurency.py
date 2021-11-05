# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~13.4")
class TestCalendarRecurrence(UpgradeCase):
    def prepare(self):
        event_ids = [
            self.env["calendar.event"]
            .create(
                {
                    "active": True,
                    "byday": "4",
                    "count": 4,
                    "day": 0,
                    "description": "Test 4th friday of month",
                    "duration": 0.5,
                    "end_type": "count",
                    "interval": 1,
                    "month_by": "day",
                    "name": "Reccuring test 1",
                    "privacy": "public",
                    "recurrency": True,
                    "rrule_type": "monthly",
                    "start": "2020-06-22 17:30:00",
                    "stop": "2020-06-22 18:00:00",
                    "week_list": "FR",
                }
            )
            .id,
            self.env["calendar.event"]
            .create(
                {
                    "active": True,
                    "byday": "5",
                    "count": 4,
                    "day": 0,
                    "description": "Test 5th friday of month",
                    "duration": 0.5,
                    "end_type": "count",
                    "interval": 1,
                    "month_by": "day",
                    "name": "Reccuring test 2",
                    "privacy": "public",
                    "recurrency": True,
                    "rrule_type": "monthly",
                    "start": "2020-06-22 17:30:00",
                    "stop": "2020-06-22 18:00:00",
                    "week_list": "FR",
                }
            )
            .id,
            self.env["calendar.event"]
            .create(
                {
                    "active": True,
                    "byday": False,
                    "count": 10,
                    "day": 1,
                    "description": "Test reccurency by week without week day",
                    "duration": 0.5,
                    "end_type": "count",
                    "interval": 1,
                    "month_by": "date",
                    "name": "Reccuring test 3",
                    "privacy": "public",
                    "recurrency": True,
                    "rrule_type": "weekly",
                    "start": "2020-06-22 18:30:00",
                    "stop": "2020-06-22 19:00:00",
                    "week_list": "FR",
                }
            )
            .id,
            self.env["calendar.event"]
            .create(
                {
                    "active": True,
                    "byday": False,
                    "count": 10,
                    "day": 1,
                    "description": "Test reccurency by week without week day nor week_list",
                    "duration": 0.5,
                    "end_type": "count",
                    "interval": 1,
                    "month_by": "date",
                    "name": "Reccuring test 4",
                    "privacy": "public",
                    "recurrency": True,
                    "rrule_type": "weekly",
                    "start": "2020-06-22 18:30:00",
                    "stop": "2020-06-22 19:00:00",
                }
            )
            .id,
            self.env["calendar.event"]
            .create(
                {
                    "active": True,
                    "byday": False,
                    "count": 10,
                    "day": 1,
                    "description": "Test reccurency without rule type",
                    "duration": 0.5,
                    "end_type": "count",
                    "interval": 1,
                    "month_by": "date",
                    "name": "Reccuring test 5",
                    "privacy": "public",
                    "recurrency": True,
                    "rrule_type": False,
                    "start": "2020-06-22 18:30:00",
                    "stop": "2020-06-22 19:00:00",
                }
            )
            .id,
            self.env["calendar.event"]
            .create(
                {
                    "active": True,
                    "byday": False,
                    "count": 10,
                    "day": 1,
                    "description": "Test reccurency without rrule",
                    "duration": 0.5,
                    "end_type": "count",
                    "interval": 1,
                    "month_by": "date",
                    "name": "Reccuring test 6",
                    "privacy": "public",
                    "recurrency": True,
                    "rrule": "",
                    "start": "2020-06-22 18:30:00",
                    "stop": "2020-06-22 19:00:00",
                }
            )
            .id,
        ]
        return {"events": event_ids}

    def check(self, init):
        return True
