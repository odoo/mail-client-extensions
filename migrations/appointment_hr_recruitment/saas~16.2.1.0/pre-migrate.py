# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "appointment_invite", "applicant_id", "int4")
    if util.column_exists(cr, "appointment_type", "applicant_id"):
        # Associate the correct lead/opportunity to the correct invitation
        cr.execute(
            """
            WITH applicants_invite AS (
                    SELECT
                            appt.applicant_id AS applicant_id,
                            invite_appt_rel.appointment_invite_id AS invite_id
                      FROM appointment_type appt
                /* appointment_invite.appointment_type_ids m2m */
                INNER JOIN appointment_invite_appointment_type_rel invite_appt_rel
                        ON invite_appt_rel.appointment_type_id = appt.id
                     WHERE appt.applicant_id IS NOT NULL
            )
            UPDATE appointment_invite invite
               SET applicant_id = applicants_invite.applicant_id
              FROM applicants_invite
             WHERE applicants_invite.invite_id = invite.id
            """
        )
        util.remove_field(cr, "appointment.type", "applicant_id")
        util.remove_field(cr, "hr.applicant", "appointment_type_id")
