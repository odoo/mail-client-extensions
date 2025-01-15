from odoo.upgrade.util import remove_record


def migrate(cr, version):
    remove_record(cr, "website_event_track.s_searchbar_000_js")
