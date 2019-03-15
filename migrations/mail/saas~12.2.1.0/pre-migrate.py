# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "ir.model.fields", "track_visibility", "tracking")
    cr.execute(
        """
            ALTER TABLE ir_model_fields
           ALTER COLUMN tracking
                   TYPE int4
                 USING CASE WHEN tracking IS NOT NULL THEN 100 END
        """
    )
    util.rename_field(cr, "mail.tracking.value", "track_sequence", "tracking_sequence")

    util.remove_field(cr, "mail.activity", "feedback")
    util.remove_field(cr, "mail.activity", "create_user_id")

    util.create_column(cr, "res_users", "out_of_office_message", "varchar")
