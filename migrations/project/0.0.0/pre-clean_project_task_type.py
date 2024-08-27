from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("17.0"):
        cr.execute(
            """
            UPDATE project_task_type ptt
               SET user_id = NULL
             WHERE EXISTS (
                           SELECT 1
                             FROM project_task_type_rel pttr
                            WHERE pttr.type_id = ptt.id
                          )
               AND ptt.user_id IS NOT NULL
            """
        )
