# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Removal of twitter hashtag leads to some views (templates) being removed
    util.remove_view(cr, "website_event_track.event_track_social")

    # Allow archiving of sponsors and get sponsor URL from partner
    util.create_column(cr, "event_sponsor", "active", "boolean")
    cr.execute("UPDATE event_sponsor SET active = true")
