from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT task.id
          FROM project_task task
         WHERE task.planned_date_begin IS NOT NULL
           AND task.planned_date_end IS NOT NULL
        """
    )
    ids = [row[0] for row in cr.fetchall()]
    util.recompute_fields(cr, "project.task", ["allocated_hours"], ids=ids, chunk_size=50)
