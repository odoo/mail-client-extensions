from odoo.upgrade import util


def migrate(cr, version):
    # The ai_tool model has been refactored. The old records don't follow the new logic.
    # These records will be dropped and new records will be registered following the new logic.
    cr.execute("SELECT server_action FROM ai_tool WHERE server_action IS NOT NULL")
    sids = [sid for (sid,) in cr.fetchall()]

    if sids:
        util.remove_records(cr, "ir.actions.server", sids)

    util.remove_model(cr, "ai.tool")
