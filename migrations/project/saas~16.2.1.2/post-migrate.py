# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Create template task for recurrence based on last task of recurrence
    env = util.env(cr)
    cr.execute(
        """ WITH recent_task_per_rec AS (
                SELECT recurrence_id,
                       MAX(id) as max_id
                  FROM project_task
                 WHERE recurrence_id IS NOT NULL
              GROUP BY recurrence_id
            )
            SELECT rec.id,
                   recent_task_per_rec.max_id
              FROM project_task_recurrence AS rec
         LEFT JOIN recent_task_per_rec
                ON rec.id = recent_task_per_rec.recurrence_id
        """
    )

    recurrence_ids, task_ids, recurrence_ids_to_unlink = [], [], []
    for recurrence_id, task_id in cr.fetchall():
        if task_id:
            recurrence_ids.append(recurrence_id)
            task_ids.append(task_id)
        else:
            recurrence_ids_to_unlink.append(recurrence_id)

    util.iter_browse(env["project.task.recurrence"], recurrence_ids_to_unlink).unlink()
    for recurrence, task in zip(
        util.iter_browse(env["project.task.recurrence"], recurrence_ids),
        util.iter_browse(env["project.task"], task_ids),
    ):
        recurrence._create_task(task_from=task)
