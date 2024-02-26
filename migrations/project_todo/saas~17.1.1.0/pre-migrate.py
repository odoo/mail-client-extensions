# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    reminder_activity_type = util.ref(cr, "project_todo.mail_activity_data_reminder")
    if reminder_activity_type:
        util.replace_record_references_batch(
            cr,
            {reminder_activity_type: util.ref(cr, "mail.mail_activity_data_todo")},
            "mail.activity.type",
            replace_xmlid=False,
        )
    util.change_field_selection_values(cr, "mail.activity.type", "category", {"reminder": "default"})
    util.remove_record(cr, "project_todo.mail_activity_data_reminder")
