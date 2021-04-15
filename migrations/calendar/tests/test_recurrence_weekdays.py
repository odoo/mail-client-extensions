# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.3")
class TestCalendarRecurrenceWeekdays(UpgradeCase):
    def prepare(self):
        weekdays = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        # mo had to be set to True in order to be able to create a new calendar.recurrence record
        data = [{"weekday": weekday, "mo": True} for weekday in weekdays]
        rrule_ids = self.env["calendar.recurrence"].create(data).ids
        return {"rrule_ids": rrule_ids}

    def check(self, init):
        rrule_ids = self.env["calendar.recurrence"].browse(init["rrule_ids"])
        self.assertTrue(all(r.weekday in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"] for r in rrule_ids))
