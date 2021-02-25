# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "calendar_event_hr_appraisal_rel", "calendar_event", "hr_appraisal")
    cr.execute(
        """
        INSERT INTO calendar_event_hr_appraisal_rel(calendar_event_id, hr_appraisal_id)
             SELECT id, res_id
               FROM calendar_event
              WHERE res_model = 'hr.appraisal'
        ON CONFLICT DO NOTHING
    """
    )
    util.remove_field(cr, "hr.appraisal", "meeting_id")
    util.remove_column(cr, "hr_appraisal", "date_final_interview")
