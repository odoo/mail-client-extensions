from odoo.upgrade import util


def migrate(cr, version):
    # is_template was added in 18.3, most DBs won't need this ever
    if util.column_exists(cr, "project_task", "is_template"):
        columns = util.get_columns(
            cr,
            "project_task_template",
            ignore=["id", "parent_id", "repeat_interval", "repeat_unit", "repeat_type"],
        )

        util.create_column(cr, "project_task_template", "_upg_orig_task_id", "integer")
        query = util.format_query(
            cr,
            """
            INSERT INTO project_task_template (
                        {columns}, _upg_orig_task_id,
                        repeat_interval,
                        repeat_unit,
                        repeat_type
                        )
                 SELECT {task_columns}, ts.id,
                        pr.repeat_interval,
                        pr.repeat_unit,
                        CASE WHEN ts.recurrence_id IS NOT NULL THEN 'forever' END
                   FROM project_task ts
              LEFT JOIN project_task_recurrence pr
                     ON ts.recurrence_id = pr.id
             WHERE ts.is_template
            """,
            columns=columns,
            task_columns=columns.using(alias="ts"),
        )
        cr.execute(query)

        cr.execute("""
            INSERT INTO project_task_template_res_users_rel (project_task_template_id, res_users_id)
            SELECT ptt.id, rel.user_id
              FROM project_task_user_rel rel
              JOIN project_task_template  ptt
                ON rel.task_id = ptt._upg_orig_task_id
        """)

        cr.execute("""
            UPDATE project_task_template pt
               SET parent_id = new_parent.id
              FROM project_task t
              JOIN project_task_template new_parent
                ON new_parent._upg_orig_task_id = t.parent_id
             WHERE pt._upg_orig_task_id = t.id
               AND t.parent_id IS NOT NULL
        """)

        cr.execute("""
            INSERT INTO project_tags_project_task_template_rel (project_task_template_id, project_tags_id)
            SELECT t.id, rel.project_tags_id
              FROM project_tags_project_task_rel rel
              JOIN project_task_template t
                ON t._upg_orig_task_id = rel.project_task_id
        """)
        cr.execute("SELECT _upg_orig_task_id, id FROM project_task_template WHERE _upg_orig_task_id IS NOT NULL")
        ids = dict(cr.fetchall())
        if ids:
            util.replace_record_references_batch(cr, ids, "project.task", "project.task.template")
        cr.execute("DELETE FROM project_task WHERE id IN %s", [tuple(ids)])

        util.remove_field(cr, "project.task.template", "_upg_orig_task_id")
        util.remove_column(cr, "project_task", "is_template")
