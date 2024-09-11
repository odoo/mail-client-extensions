from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_event_track_live.tracks_display_list")
