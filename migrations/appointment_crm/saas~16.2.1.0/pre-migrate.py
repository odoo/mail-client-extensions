from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "appointment_invite", "opportunity_id", "int4")
    # Associate the correct lead/opportunity to the correct invitation
    cr.execute(
        """
        WITH opportunities_invite AS (
                SELECT
                        appt.opportunity_id AS opp_id,
                        invite_appt_rel.appointment_invite_id AS invite_id
                  FROM appointment_type appt
            /* appointment_invite.appointment_type_ids m2m */
            INNER JOIN appointment_invite_appointment_type_rel invite_appt_rel
                    ON invite_appt_rel.appointment_type_id = appt.id
                 WHERE appt.category = 'custom' AND appt.opportunity_id IS NOT NULL
        )
        UPDATE appointment_invite invite
           SET opportunity_id = opp_invite.opp_id
          FROM opportunities_invite opp_invite
         WHERE opp_invite.invite_id = invite.id
        """
    )
    util.remove_field(cr, "appointment.type", "opportunity_id")
