# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    to_do_activity_type = util.ref(cr, "mail.mail_activity_data_todo")
    reminder_activity_type = util.ref(cr, "project_todo.mail_activity_data_reminder")
    if reminder_activity_type:
        query = cr.mogrify(
            """
            UPDATE mail_activity
               SET activity_type_id = %s
             WHERE activity_type_id = %s
            """,
            [to_do_activity_type, reminder_activity_type],
        ).decode()
        util.explode_execute(cr, query, table="mail_activity")
    util.remove_record(cr, "project_todo.mail_activity_data_reminder")
    util.change_field_selection_values(cr, "mail.activity.type", "category", {"reminder": "default"})
