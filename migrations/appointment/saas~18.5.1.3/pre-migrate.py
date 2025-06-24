from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "appointment.invite", "has_identical_config")
    util.remove_menus(cr, [util.ref(cr, "appointment.menu_schedule_report_all_events")])

    util.remove_menus(cr, [util.ref(cr, "appointment.menu_appointment_type_custom")])
    util.remove_record(cr, "appointment.appointment_type_action_custom")
    util.remove_record(cr, "appointment.appointment_type_view_tree_invitation")

    cr.execute("""
        DELETE FROM appointment_slot
              WHERE slot_type = 'unique'
                AND ((start_datetime IS NULL OR end_datetime IS NULL) OR
                     (start_datetime > end_datetime)
                    )
    """)

    # Set a question_type to questions having none. Use 'char' as default, and 'selection' if it has answers.
    cr.execute("""
        WITH select_questions AS (
            SELECT question_id
              FROM appointment_answer
          GROUP BY question_id
        )
        UPDATE appointment_question aq
           SET question_type = 'select'
          FROM select_questions
         WHERE aq.id = select_questions.question_id
           AND aq.question_type IS NULL
    """)

    util.explode_execute(
        cr,
        """
        UPDATE appointment_question
           SET question_type = 'char'
         WHERE question_type IS NULL
        """,
        table="appointment_question",
    )

    util.create_column(cr, "appointment_question", "is_reusable", "boolean")
    util.create_column(cr, "appointment_question", "is_default", "boolean")

    # Bump sequence of existing questions, Insert default question, of new 'phone' question_type.
    cr.execute("UPDATE appointment_question SET sequence = sequence + 1")
    cr.execute(
        """
        INSERT INTO appointment_question (name, question_type, question_required, sequence, placeholder, is_reusable, is_default)
                    VALUES('{"en_US": "Phone number"}'::jsonb, 'phone', TRUE, 0, '{"en_US": "e.g. +1 555-555-5555"}'::jsonb, TRUE, TRUE)
          RETURNING id
        """
    )
    phone_question_id = cr.fetchone()[0]
    # Ensure appointment_question_phone is linked to the phone question
    cr.execute(
        """
        INSERT INTO ir_model_data (module, name, res_id, model, noupdate)
             VALUES ('appointment', 'appointment_question_phone', %s, 'appointment.question', 't')
        """,
        [phone_question_id],
    )

    # Populate the relational table with existing couples and add the phone question to all appointments.
    util.create_m2m(cr, "appointment_type_appointment_question_rel", "appointment_type", "appointment_question")
    cr.execute(
        """
        INSERT INTO appointment_type_appointment_question_rel (appointment_type_id, appointment_question_id)
             SELECT at.id, %s
               FROM appointment_type at
          UNION ALL
             SELECT aq.appointment_type_id, aq.id
               FROM appointment_question aq
              WHERE aq.appointment_type_id IS NOT NULL
        """,
        [phone_question_id],
    )

    util.remove_column(cr, "appointment_question", "appointment_type_id")
    util.rename_field(cr, "appointment.question", "appointment_type_id", "appointment_type_ids")
    util.rename_xmlid(cr, "appointment.menu_schedule_report", "appointment.menu_appointment_reporting")
    util.rename_xmlid(
        cr,
        "appointment.appointment_answer_input_action_from_question",
        "appointment.appointment_answer_input_action",
    )
