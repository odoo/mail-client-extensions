from odoo.upgrade import util


def migrate(cr, version):
    query = """
        SELECT task.id
          FROM project_task task
         WHERE task.planned_date_begin IS NOT NULL
           AND task.planned_date_end IS NOT NULL
        """
    util.recompute_fields(cr, "project.task", ["allocated_hours"], query=query, chunk_size=50)
