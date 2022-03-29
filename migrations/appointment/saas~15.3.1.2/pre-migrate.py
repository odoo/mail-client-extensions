# -*- coding: utf-8 -*-

from odoo.upgrade import util
from odoo.upgrade.util.records import _remove_records


def migrate(cr, version):
    # Make answer_ids a O2M instead of a M20
    util.create_column(cr, "calendar_appointment_answer", "question_id", "integer")
    # --- Temporary column to keep track of which record duplicates originate
    util.create_column(cr, "calendar_appointment_answer", "_tmp_original_answer_id", "integer")
    # --- Set question_id, duplicate answers used more than once and remove relational table
    cr.execute(
        """
            WITH ranked_rel AS (
                SELECT question_id, answer_id, ROW_NUMBER() OVER (PARTITION BY answer_id ORDER BY question_id) rank
                  FROM calendar_appointment_question_answer_rel
            ),
            _ AS (
                UPDATE calendar_appointment_answer ans
                   SET question_id = rel.question_id
                  FROM ranked_rel rel
                 WHERE ans.id = rel.answer_id
                   AND rel.rank = 1
            )
            INSERT INTO calendar_appointment_answer (name, create_date, create_uid, question_id, _tmp_original_answer_id)
                 SELECT ans.name, ans.create_date, ans.create_uid, rel.question_id, ans.id
                   FROM calendar_appointment_answer ans
                   JOIN ranked_rel rel
                     ON ans.id = rel.answer_id
                    AND rel.rank > 1
        """
    )
    cr.execute("DROP TABLE calendar_appointment_question_answer_rel")

    # --- Duplicate the translations for duplicated answers if any and remove temporary column
    cr.execute(
        """
            INSERT INTO ir_translation (name, res_id, lang, type, src, value, module, state, comments)
                 SELECT irt.name, ans.id, irt.lang, irt.type, irt.src, irt.value, irt.module, irt.state, irt.comments
                   FROM calendar_appointment_answer ans
                   JOIN ir_translation irt
                     ON irt.res_id = ans._tmp_original_answer_id
                  WHERE irt.name = 'calendar.appointment.answer,name'
                    AND ans._tmp_original_answer_id IS NOT NULL
        """
    )
    util.remove_column(cr, "calendar_appointment_answer", "_tmp_original_answer_id")

    # --- Delete unused answers
    cr.execute("SELECT id FROM calendar_appointment_answer WHERE question_id IS NULL")
    ids = [aid for aid, in cr.fetchall()]
    _remove_records(cr, "calendar.appointment.answer", ids)

    util.create_column(cr, "calendar_appointment_answer", "sequence", "integer", default=10)

    # Mutate Char location to M2O location_id
    util.create_column(cr, "calendar_appointment_type", "location_id", "integer")

    # --- The new `location_id` field will reference a partner (see Event.Event `venue`).
    # --- During migration, partners are created so that their contact address will be formatted
    # --- into the current appointment type `location` field.
    cr.execute(
        """
        WITH new_partners AS (
                INSERT INTO res_partner(name, display_name, active, type)
            SELECT DISTINCT t.location, t.location, true, 'contact'
                       FROM calendar_appointment_type t
                      WHERE t.location IS NOT NULL
                        AND t.location != ''
                  RETURNING id, name
        )
        UPDATE calendar_appointment_type t
           SET location_id = p.id
          FROM new_partners p
         WHERE p.name = t.location
    """
    )

    util.remove_field(cr, "calendar.appointment.type", "location")
