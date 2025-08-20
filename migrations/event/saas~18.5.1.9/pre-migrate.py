from odoo.upgrade import util


def migrate(cr, version):
    query = cr.mogrify(
        """
        UPDATE event_event
           SET kanban_state = 'cancel'
         WHERE stage_id = %s
    """,
        (util.ref(cr, "event.event_stage_cancelled"),),
    ).decode()
    util.explode_execute(cr, query, table="event_event")
    util.remove_field(cr, "event.stage", "legend_normal")
    util.remove_field(cr, "event.stage", "legend_done")
    util.remove_field(cr, "event.stage", "legend_blocked")
    util.remove_field(cr, "event.event", "legend_normal")
    util.remove_field(cr, "event.event", "legend_done")
    util.remove_field(cr, "event.event", "legend_blocked")
    util.remove_field(cr, "event.event", "kanban_state_label")

    util.create_m2m(cr, "event_event_event_question_rel", "event_event", "event_question")
    cr.execute(
        """
        INSERT INTO event_event_event_question_rel (event_question_id, event_event_id)
             SELECT id, event_id
               FROM event_question
              WHERE event_id IS NOT NULL
        """
    )
    util.remove_column(cr, "event_question", "event_id")
    util.rename_field(cr, "event.question", "event_id", "event_ids")

    util.create_m2m(cr, "event_question_event_type_rel", "event_question", "event_type")
    cr.execute(
        """
        INSERT INTO event_question_event_type_rel (event_question_id, event_type_id)
             SELECT id, event_type_id
               FROM event_question
              WHERE event_type_id IS NOT NULL
        """
    )
    util.remove_column(cr, "event_question", "event_type_id")
    util.rename_field(cr, "event.question", "event_type_id", "event_type_ids")

    util.create_column(cr, "event_question", "is_reusable", "boolean", default=True)

    util.rename_xmlid(cr, "event.act_event_slot_from_event", "event.event_slot_action_from_event")
