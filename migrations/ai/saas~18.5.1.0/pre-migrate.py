from odoo.upgrade import util


def migrate(cr, version):
    # The ai_tool model has been refactored. The old records don't follow the new logic.
    # These records will be dropped and new ai_tool records will be registered following the new logic.
    cr.execute(
        "SELECT array_agg(id), array_agg(DISTINCT server_action) FILTER (WHERE server_action IS NOT NULL) FROM ai_tool"
    )
    tids, sids = cr.fetchone()
    if tids:
        util.remove_records(cr, "ai.tool", tids)
    if sids:
        util.remove_records(cr, "ir.actions.server", sids)

    util.remove_field(cr, "ai.tool", "result_prompt")
    util.remove_field(cr, "ai.tool", "server_action")
    util.remove_field(cr, "ai.tool", "input_schema")
    util.remove_field(cr, "ai.tool", "formatted_name")
    util.make_field_non_stored(cr, "ai.tool", "description")
