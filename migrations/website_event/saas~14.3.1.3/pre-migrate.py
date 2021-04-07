# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    # Clean the ACLs XMLID
    acl_name_changes = {
        "access_event_type_public": "event_type",
        "access_event_category_public": "event_tag_category",
        "access_event_tag_public": "event_tag",
        "access_website_event_menu_public": "website_event_menu",
        "website_visitor_access_event_user": "website_visitor_user",
    }
    for old_name, new_name in acl_name_changes.items():
        util.rename_xmlid(cr, f"website_event.{old_name}", f"website_event.access_{new_name}")

    # Remove ACLs
    util.remove_record(cr, "website_event.access_event_event_public")
    util.remove_record(cr, "website_event.access_event_event_portal")
    util.remove_record(cr, "website_event.access_event_event_ticket_public")
    util.remove_record(cr, "website_event.access_event_event_ticket_portal")
    util.remove_record(cr, "website_event.access_website_event_menu_manager")
