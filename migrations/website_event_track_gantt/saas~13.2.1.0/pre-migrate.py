# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr, "website_event_track_gantt.view_event_track_gantt", "website_event_track_gantt.event_track_view_gantt"
    )
