# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    # Clean the ACLs XMLID
    acl_name_changes = {
        "event_portal": "event",
        "registration": "registration_user",
        "registration_all": "registration",
        "mail": "mail_user",
        "type_mail_event_manager": "type_mail_manager",
        "category_manager": "tag_category_manager",
        "tag": "tag_user",
    }
    for old_name, new_name in acl_name_changes.items():
        util.rename_xmlid(cr, f"event.access_event_{old_name}", f"event.access_event_{new_name}")
