from odoo.upgrade import util
from odoo.upgrade.util.inconsistencies import break_recursive_loops


def migrate(cr, version):
    util.remove_record(cr, "project.action_server_view_my_task")

    util.remove_field(cr, "res.config.settings", "group_project_rating")
    util.remove_field(cr, "res.config.settings", "group_project_recurring_tasks")
    util.remove_field(cr, "res.config.settings", "group_project_task_dependencies")
    util.remove_field(cr, "res.config.settings", "group_project_milestone")

    util.remove_record(cr, "project.group_project_rating")
    util.create_column(cr, "project_project", "allow_recurring_tasks", "boolean")

    util.remove_field(cr, "project.task.type", "disabled_rating_warning")
    util.create_column(cr, "project_task_type", "rating_active", "boolean")
    util.create_column(cr, "project_task_type", "rating_status", "varchar")
    util.create_column(cr, "project_task_type", "rating_status_period", "varchar")
    util.create_column(cr, "project_task_type", "rating_request_deadline", "timestamp without time zone")

    # Fetch the project stages data and group by project configuration (rating_active, rating_status, rating_status_period)
    # Also retrieve the project_ids for each stage and configuration
    # The idea to have a stage per configuration, thus duplicating stages if needed
    columns = util.get_columns(
        cr,
        "project_task_type",
        ignore=["id", "rating_active", "rating_status", "rating_status_period", "rating_request_deadline"],
    )
    util.create_column(cr, "project_task_type", "_upg_project_ids", "integer[]")
    util.create_column(cr, "project_task_type", "_upg_original_id", "integer")

    query = util.format_query(
        cr,
        """
          WITH groups AS (
            SELECT ptt.id AS type_id,
                   pp.rating_active,
                   CASE WHEN pp.rating_active THEN pp.rating_status ELSE 'stage' END AS rating_status,
                   CASE WHEN pp.rating_active AND pp.rating_status='periodic' THEN pp.rating_status_period ELSE 'monthly' END AS rating_status_period,
                   NOW() AT TIME ZONE 'UTC' AS rating_request_deadline,
                   ARRAY_AGG(DISTINCT ptr.project_id) AS project_ids,
                   ROW_NUMBER() OVER (PARTITION BY ptt.id ORDER BY ptt.id) AS rn
              FROM project_task_type ptt
              JOIN project_task_type_rel ptr
                ON ptt.id = ptr.type_id
              JOIN project_project pp
                ON pp.id = ptr.project_id
             WHERE ptt.rating_template_id IS NOT NULL
          GROUP BY 1, 2, 3, 4
        ), new_stages AS (
            -- new stages duplicated from the first group
   INSERT INTO project_task_type ({columns}, rating_active, rating_status, rating_status_period, rating_request_deadline, _upg_project_ids, _upg_original_id)
            SELECT {ptt_columns},
                   groups.rating_active,
                   groups.rating_status,
                   groups.rating_status_period,
                   groups.rating_request_deadline,
                   groups.project_ids,
                   ptt.id
              FROM project_task_type ptt
              JOIN groups
                ON ptt.id = groups.type_id
             WHERE groups.rn > 1
         RETURNING id, _upg_project_ids, _upg_original_id
        ), link_stages AS (
            -- link new stages to their projects per group
   INSERT INTO project_task_type_rel(type_id, project_id)
            SELECT id, unnest(_upg_project_ids)
              FROM new_stages
         RETURNING project_id
        ), delete_stages AS (
            -- remove the projects where duplication occured for the stages that we keep (the original ones)
        DELETE FROM project_task_type_rel ptr
             USING groups
             WHERE ptr.type_id = groups.type_id
               AND groups.rn = 1
               AND ptr.project_id <> ALL(groups.project_ids)
        ), updated_stages AS (
            -- update the original stages configuration
        UPDATE project_task_type ptt
               SET rating_active = groups.rating_active,
                   rating_status = groups.rating_status,
                   rating_status_period = groups.rating_status_period,
                   rating_request_deadline = groups.rating_request_deadline
              FROM groups
             WHERE ptt.id = groups.type_id
               AND groups.rn = 1
        ), updated_tasks AS (
            -- update the task links to duplicated stages
        UPDATE project_task pt
               SET stage_id = ns.id
              FROM new_stages ns
             WHERE pt.stage_id = ns._upg_original_id
               AND pt.project_id = ANY(ns._upg_project_ids)
        )
   SELECT DISTINCT pp.id, pp.name->'en_US'
              FROM link_stages ls
              JOIN project_project pp
                ON ls.project_id = pp.id
        """,
        columns=columns,
        ptt_columns=columns.using(alias="ptt"),
    )
    cr.execute(query)

    updated_projects = cr.fetchall()
    if updated_projects:
        li = "\n".join(
            [
                "<li>{}</li>".format(util.get_anchor_link_to_record("project.project", id_, name))
                for id_, name in updated_projects
            ]
        )
        util.add_to_migration_reports(
            message=f"""
                <details>
                    <summary>
                    Project customer rating data has been moved from projects to task stages.
                    Some stages may have been created to accommodate the different combinations
                    of rating data. In the new stages the Rating request deadline was reset.
                    Please check and maybe re-configure the stages on the projects below.
                    </summary>
                    <ul>{li}</ul>
                </details>
            """,
            category="Project",
            format="html",
        )

    # Populate recurring 'allow_recurring_tasks' field on projects
    # Set it to True if the project has at least one task with recurring_task=True
    cr.execute(
        """
        WITH _recurring_projects AS (
            SELECT project_id
              FROM project_task
             WHERE recurring_task
          GROUP BY project_id
        )
      UPDATE project_project p
               SET allow_recurring_tasks = TRUE
              FROM _recurring_projects r
             WHERE r.project_id = p.id
        """
    )

    # Remove temporary columns
    util.remove_column(cr, "project_task_type", "_upg_project_ids")
    util.remove_column(cr, "project_task_type", "_upg_original_id")

    # Remove project customer rating fields
    util.remove_field(cr, "project.project", "rating_request_deadline")
    util.remove_field(cr, "project.project", "rating_active")
    util.remove_field(cr, "project.project", "rating_status")
    util.remove_field(cr, "project.project", "rating_status_period")
    util.remove_menus(
        cr,
        [
            util.ref(cr, "project.project_menu_config_project_templates"),
            util.ref(cr, "project.project_menu_config_task_templates"),
        ],
    )
    for record in [
        "project.project_task_templates_action",
        "project.project_task_templates_action_list",
        "project.project_task_templates_action_kanban",
        "project.project_templates_action",
        "project.project_templates_action_list",
        "project.project_templates_action_kanban",
        "project.project_templates_action_form",
    ]:
        util.remove_record(cr, record)
    break_recursive_loops(cr, "project.task", "parent_id")
    util.create_column(cr, "project_task", "has_template_ancestor", "boolean")
    if util.column_exists(cr, "project_task", "is_template"):
        cr.execute(
            """
            WITH RECURSIVE tmpl_anc AS (
                SELECT t.id
                  FROM project_task t
                 WHERE t.is_template

                 UNION

                SELECT t.id
                  FROM project_task t
                  JOIN tmpl_anc p
                    ON t.parent_id = p.id
            ) UPDATE project_task t
                 SET has_template_ancestor = True
                FROM tmpl_anc
               WHERE t.id = tmpl_anc.id
            """
        )
