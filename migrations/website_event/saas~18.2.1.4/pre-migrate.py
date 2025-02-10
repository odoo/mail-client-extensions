from odoo.upgrade.util import remove_record, remove_view


def migrate(cr, version):
    remove_record(cr, "website_event.s_events_000_js")
    remove_record(cr, "website_event.s_searchbar_000_js")

    remove_view(cr, "website_event.event_event_view_form_add")
