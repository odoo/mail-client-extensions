# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "ir_act_server", "activity_type_id", "integer")
    util.create_column(cr, "ir_act_server", "activity_summary", "varchar")
    util.create_column(cr, "ir_act_server", "activity_note", "text")
    util.create_column(cr, "ir_act_server", "activity_date_deadline_range", "integer")
    util.create_column(cr, "ir_act_server", "activity_date_deadline_range_type", "varchar")
    util.create_column(cr, "ir_act_server", "activity_user_type", "varchar")
    util.create_column(cr, "ir_act_server", "activity_user_id", "integer")
    util.create_column(cr, "ir_act_server", "activity_user_field_name", "varchar")
    cr.execute("UPDATE ir_act_server set activity_user_type='specific'")

    util.create_column(cr, "mail_activity_type", "delay_unit", "varchar")
    util.create_column(cr, "mail_activity_type", "delay_from", "varchar")
    util.create_column(cr, "mail_activity_type", "decoration_type", "varchar")
    util.create_column(cr, "mail_activity_type", "default_next_type_id", "integer")
    util.create_column(cr, "mail_activity_type", "force_next", "boolean")
    util.rename_field(cr, "mail.activity.type", "days", "delay_count")
    cr.execute("UPDATE mail_activity_type set delay_unit='days', delay_from='previous_activity', force_next=FALSE")

    util.create_column(cr, "mail_activity", "create_user_id", "integer")
    cr.execute("UPDATE mail_activity SET create_user_id=create_uid")

    util.create_column(cr, "mail_tracking_value", "track_sequence", "integer")
