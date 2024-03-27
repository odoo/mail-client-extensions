from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.column_exists(cr, "res_users", "action_id"):
        cr.execute(
            """
            UPDATE res_users
               SET action_id = NULL
             WHERE action_id IS NOT NULL
               AND NOT EXISTS (
                    SELECT 1
                      FROM ir_actions
                     WHERE ir_actions.id = res_users.action_id
                   )
            """
        )
