from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_event.template_location")
    util.remove_view(cr, "website_event.default_page")
    util.remove_view(cr, "website_event.404")
    util.remove_field(cr, "event.event", "location_menu")
    util.change_field_selection_values(cr, "website.event.menu", "menu_type", {"location": "other"})
    util.rename_field(cr, "event.event", "location_menu_ids", "other_menu_ids")
