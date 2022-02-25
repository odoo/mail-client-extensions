# -*- coding: utf-8 -*-

from odoo.upgrade import util
from odoo.upgrade.util.records import _remove_records


def migrate(cr, version):
    eb = util.expand_braces

    util.create_column(cr, "calendar_appointment_type", "is_published", "boolean", default=True)
    util.move_field_to_module(cr, "calendar.appointment.type", "is_published", "website_appointment", "appointment")

    util.remove_model(cr, "calendar.appointment.share")

    # Rename models & fields
    util.rename_model(cr, "calendar.appointment.type", "appointment.type")
    util.rename_model(cr, "calendar.appointment.slot", "appointment.slot")
    util.rename_model(cr, "calendar.appointment.question", "appointment.question")
    util.rename_model(cr, "calendar.appointment.answer", "appointment.answer")

    cr.execute("ALTER TABLE calendar_appointment_question_answer_rel RENAME TO appointment_question_answer_rel")
    cr.execute(
        "ALTER TABLE appointment_type_country_rel RENAME COLUMN calendar_appointment_type_id TO appointment_type_id"
    )
    cr.execute(
        "ALTER TABLE appointment_type_res_users_rel RENAME COLUMN calendar_appointment_type_id TO appointment_type_id"
    )

    # Rename of xmlid
    renames = [
        "appointment.{calendar_,}appointment_answer_view_form",
        "appointment.{calendar_,}appointment_slot_view_form",
        "appointment.{calendar_,}appointment_type_view_search",
        "appointment.{calendar_,}appointment_type_view_kanban",
        "appointment.{calendar_,}appointment_type_view_form",
        "appointment.{calendar_,}appointment_type_view_tree",
        "appointment.{calendar_,}appointment_type_view_tree_invitation",
        "appointment.{calendar_,}appointment_type_action",
        "appointment.{calendar_,}appointment_type_action_custom_and_work_hours",
        "appointment.menu_{calendar_,}appointment_type_custom_and_work_hours",
        "appointment.group_{calendar,appointment}_manager",
        "appointment.access_{calendar_,}appointment_type_all",
        "appointment.access_{calendar_,}appointment_type_manager",
        "appointment.access_{calendar_,}appointment_slot_user",
        "appointment.access_{calendar_,}appointment_slot_manager",
        "appointment.access_{calendar_,}appointment_question_all",
        "appointment.access_{calendar_,}appointment_question_manager",
        "appointment.access_{calendar_,}appointment_question_answer_all",
        "appointment.access_{calendar_,}appointment_question_answer_manager",
        "appointment.access_{calendar_,}appointment_question_answer_input_all",
        "appointment.access_{calendar_,}appointment_question_answer_input_manager",
    ]
    for rename in renames:
        util.rename_xmlid(cr, *eb(rename))

    util.remove_view(cr, "appointment.calendar_appointment_share_view_form")
    util.remove_view(cr, "appointment.calendar_appointment_insert_share_view_form")

    # Make answer_ids a O2M instead of a M20
    util.create_column(cr, "appointment_answer", "question_id", "integer")
    # --- Temporary column to keep track of which record duplicates originate
    util.create_column(cr, "appointment_answer", "_tmp_original_answer_id", "integer")
    # --- Set question_id, duplicate answers used more than once and remove relational table
    cr.execute(
        """
            WITH ranked_rel AS (
                SELECT question_id, answer_id, ROW_NUMBER() OVER (PARTITION BY answer_id ORDER BY question_id) rank
                  FROM appointment_question_answer_rel
            ),
            _ AS (
                UPDATE appointment_answer ans
                   SET question_id = rel.question_id
                  FROM ranked_rel rel
                 WHERE ans.id = rel.answer_id
                   AND rel.rank = 1
            )
            INSERT INTO appointment_answer (name, create_date, create_uid, question_id, _tmp_original_answer_id)
                 SELECT ans.name, ans.create_date, ans.create_uid, rel.question_id, ans.id
                   FROM appointment_answer ans
                   JOIN ranked_rel rel
                     ON ans.id = rel.answer_id
                    AND rel.rank > 1
        """
    )
    cr.execute("DROP TABLE appointment_question_answer_rel")

    # --- Duplicate the translations for duplicated answers if any and remove temporary column
    cr.execute(
        """
            INSERT INTO ir_translation (name, res_id, lang, type, src, value, module, state, comments)
                 SELECT irt.name, ans.id, irt.lang, irt.type, irt.src, irt.value, irt.module, irt.state, irt.comments
                   FROM appointment_answer ans
                   JOIN ir_translation irt
                     ON irt.res_id = ans._tmp_original_answer_id
                  WHERE irt.name = 'appointment.answer,name'
                    AND ans._tmp_original_answer_id IS NOT NULL
        """
    )
    util.remove_column(cr, "appointment_answer", "_tmp_original_answer_id")

    # --- Delete unused answers
    cr.execute("SELECT id FROM appointment_answer WHERE question_id IS NULL")
    ids = [aid for aid, in cr.fetchall()]
    _remove_records(cr, "appointment.answer", ids)

    util.create_column(cr, "appointment_answer", "sequence", "integer", default=10)

    # Mutate Char location to M2O location_id
    util.create_column(cr, "appointment_type", "location_id", "integer")

    # --- The new `location_id` field will reference a partner (see Event.Event `venue`).
    # --- During migration, partners are created so that their contact address will be formatted
    # --- into the current appointment type `location` field.
    cr.execute(
        """
        WITH new_partners AS (
                INSERT INTO res_partner(name, display_name, active, type)
            SELECT DISTINCT t.location, t.location, true, 'contact'
                       FROM appointment_type t
                      WHERE t.location IS NOT NULL
                        AND t.location != ''
                  RETURNING id, name
        )
        UPDATE appointment_type t
           SET location_id = p.id
          FROM new_partners p
         WHERE p.name = t.location
    """
    )

    util.remove_field(cr, "appointment.type", "location")
