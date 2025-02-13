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
