# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    some timezones doesn't exists in all pytz versions
    """
    if util.column_exists(cr, "resource_resource", "tz"):
        tz_convert = [
            ["US/Pacific-New", "US/Pacific"],
        ]
        for old, new in tz_convert:
            cr.execute("UPDATE resource_resource SET tz=%s WHERE tz=%s", [new, old])
