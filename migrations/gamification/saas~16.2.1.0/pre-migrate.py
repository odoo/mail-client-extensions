from odoo.upgrade import util


def migrate(cr, version):
    cron_id = util.rename_xmlid(cr, "gamification.ir_cron_consolidate_last_month", "gamification.ir_cron_consolidate")
    if cron_id:
        cr.execute(
            """
            UPDATE ir_act_server s
               SET code='model._consolidate_cron()'
              FROM ir_cron c
             WHERE c.ir_actions_server_id = s.id
               AND c.id = %s
            """,
            [cron_id],
        )

    util.create_column(cr, "gamification_karma_tracking", "origin_ref", "varchar")
    util.create_column(cr, "gamification_karma_tracking", "origin_ref_model_name", "varchar")
    util.create_column(cr, "gamification_karma_tracking", "reason", "text")
