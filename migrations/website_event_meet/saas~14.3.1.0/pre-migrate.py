# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    # Clean the ACLs XMLID
    acl_name_changes = {
        "event_meeting_room_access_all": "event_meeting_room",
        "event_meeting_room_access_user": "event_meeting_room_user",
        "chat_room_access_event_user": "chat_room_user",
    }
    for old_name, new_name in acl_name_changes.items():
        util.rename_xmlid(cr, f"website_event_meet.{old_name}", f"website_event_meet.access_{new_name}")

    # Remove ACLs
    util.remove_record(cr, "website_event_meet.access_event_meeting_room_manager")
    util.remove_record(cr, "website_event_meet.access_chat_room_manager")
