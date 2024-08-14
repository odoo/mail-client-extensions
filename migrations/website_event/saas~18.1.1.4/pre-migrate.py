from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_event.events_search_box_input")
    util.remove_view(cr, "website_event.events_search_box")
