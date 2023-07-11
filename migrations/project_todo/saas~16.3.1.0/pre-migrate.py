# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    """
    The app Notes is removed and replaced by the app Todo. This implies that the following model conversions
    need to be realized:
    1. note.note -> project.task
    2. note.stage -> project.task.type
    3. note.tag -> project.tags

    Models related to note module are removed at the end of the migration.
    """

    # -------------------------- 0. Pre check --------------------------

    # If module payroll is installed some additional actions need to be performed
    # to avoid the conversion of the payroll note to project.task
    payroll_tag_id = util.module_installed(cr, "hr_payroll") and util.ref(cr, "hr_payroll.payroll_note_tag")

    # ----------- 1. Removed unused field on mail.activity -------------

    util.remove_field(cr, "mail.activity", "note_id")

    # ------------- 2. Converting note.tag -> project.tags -------------

    # keeping track of old ids to update M2X relations
    util.create_column(cr, "project_tags", "_upg_note_tag_id", "int4")
    query_filter = ""
    if payroll_tag_id:
        query_filter = cr.mogrify("WHERE id != %s", [payroll_tag_id]).decode()
    cr.execute(
        f"""
        INSERT INTO project_tags (_upg_note_tag_id, name, color)
        SELECT id, name, color
          FROM note_tag
          {query_filter}
   ON CONFLICT (name) DO UPDATE
           SET _upg_note_tag_id = EXCLUDED._upg_note_tag_id
        """
    )

    # -------- 3. Converting note.stage -> project.task.type -----------

    # A. Users who have no personal stages in project: copy personal stage from Notes
    # and keep track of the old ids to update M2X relations
    util.create_column(cr, "project_task_type", "_upg_note_stage_id", "int4")

    # Copy the new stages from note.stage to project.task.type
    cr.execute(
        """
        INSERT INTO project_task_type (name, sequence, user_id, fold, active, create_uid, write_uid, create_date, write_date, _upg_note_stage_id)
             SELECT name, sequence, user_id, fold, true, create_uid, write_uid, create_date, write_date, id
               FROM note_stage s
              WHERE NOT EXISTS (SELECT 1 FROM project_task_type ptt WHERE ptt.user_id = s.user_id)
        """
    )

    # B. Users who have no personal stage, neither in Notes, nor in Project: Create the default ones
    default_stages = util.env(cr)["project.task"]._get_default_personal_stage_create_vals(None)
    queries = []
    for stage in default_stages:
        queries.append(
            cr.mogrify(
                """
            SELECT jsonb_build_object('en_US', %s), %s, id, %s, true
              FROM users
                 """,
                [stage["name"], stage["sequence"], stage["fold"]],
            ).decode()
        )

    query = """
      WITH users AS (
          SELECT id
            FROM res_users
           WHERE NOT share
             AND NOT EXISTS (
                SELECT 1
                  FROM project_task_type
                 WHERE project_task_type.user_id = res_users.id
             )
      )
      INSERT INTO project_task_type (name, sequence, user_id, fold, active)
      {}
    """.format(
        " UNION ".join(queries)
    )
    cr.execute(query)

    # ----------- 4. Converting note.note -> project.task --------------

    # keeping track of old ids to update M2X relations
    util.create_column(cr, "project_task", "_upg_note_id", "int4")
    main_company = util.ref(cr, "base.main_company")
    # set company_id to the default one of the user if missing (required in project)
    cr.execute(
        """
        UPDATE note_note n
           SET company_id = u.company_id
          FROM res_users u
         WHERE u.id = n.user_id
           AND n.company_id IS NULL
        """
    )
    # while converting note to task, mapping boolean value of 'open' to selection field 'state'
    # and performing the computation of is_closed
    # open = True  -> state = '01_in_progress', is_closed = False
    # open = False -> state = '1_done', is_closed = True
    extra_query = ""

    if payroll_tag_id:
        extra_query = cr.mogrify(
            "WHERE NOT EXISTS (SELECT 1 FROM note_tags_rel WHERE tag_id = %s AND note_id = n.id)", [payroll_tag_id]
        ).decode()
    is_closed_column_exists = not util.version_gte("saas~16.4")
    cr.execute(
        f"""
        INSERT INTO project_task (name, company_id, description, sequence, color, create_uid,
                                  write_uid, create_date, write_date, active, state, {'is_closed,' if is_closed_column_exists else ''} _upg_note_id)
             SELECT n.name, COALESCE(n.company_id, cuid.company_id, {main_company}), n.memo, n.sequence, n.color, n.create_uid,
                    n.write_uid, n.create_date, n.write_date, TRUE, (
                    CASE
                        WHEN n.open
                        THEN '01_in_progress'
                        ELSE '1_done'
                    END
                    ),
                    {'NOT(n.open),' if is_closed_column_exists else ''}
                    n.id
               FROM note_note AS n
          LEFT JOIN res_users AS cuid
                 ON cuid.id = n.create_uid
        """
        + extra_query
    )

    # Stop migration if no notes need to be converted
    if not cr.rowcount:
        return

    util.add_to_migration_reports(
        "All the notes of this database (records of model note.note) have been converted to tasks (project.task) that can be seen in both apps Project and To-do. Deleting those apps will result in the loss of these data."
    )

    # ---------------- 5. Populate relations tables --------------------

    # A. task - user - personal stage
    # add owner of notes as assignees
    cr.execute(
        """
        INSERT INTO project_task_user_rel (task_id, user_id, stage_id)
             SELECT task.id, n.user_id, ptt.id
               FROM note_note AS n
               JOIN project_task AS task
                 ON task._upg_note_id=n.id
          LEFT JOIN note_stage_rel AS rel
                 ON n.id = rel.note_id
          LEFT JOIN note_stage AS stage
                 ON stage.id=rel.stage_id
          LEFT JOIN project_task_type AS ptt
                 ON rel.stage_id = ptt._upg_note_stage_id
                AND ptt.user_id = stage.user_id
              WHERE n.user_id IS NOT NULL
                AND (stage.user_id = n.user_id OR rel.stage_id IS NULL)
        """
    )
    # add followers of notes as assigness and update followers in mail_followers
    # case a: Followers have already put the note in a stage
    cr.execute(
        """
        INSERT INTO project_task_user_rel (task_id, user_id, stage_id)
             SELECT task.id, ru.id, ptt.id
               FROM mail_followers AS mail
               JOIN project_task AS task
                 ON task._upg_note_id=mail.res_id
         INNER JOIN res_users AS ru
                 ON ru.partner_id = mail.partner_id
          LEFT JOIN note_stage_rel AS rel
                 ON mail.res_id = rel.note_id
          LEFT JOIN project_task_type AS ptt
                 ON rel.stage_id = ptt._upg_note_stage_id
              WHERE (ptt.user_id = ru.id)
                AND mail.res_model = 'note.note'
                AND (task.id, ru.id) NOT IN (
                        SELECT task_id, user_id
                          FROM project_task_user_rel)
        """
    )
    # case b: Followers have not yet put the note in a stage
    cr.execute(
        """
        INSERT INTO project_task_user_rel (task_id, user_id)
             SELECT task.id, ru.id
               FROM mail_followers AS mail
               JOIN project_task AS task
                 ON task._upg_note_id=mail.res_id
         INNER JOIN res_users AS ru
                 ON ru.partner_id = mail.partner_id
              WHERE mail.res_model = 'note.note'
                AND (task.id, ru.id) NOT IN (
                        SELECT task_id, user_id
                          FROM project_task_user_rel)
        """
    )
    # Update personal stage with the default one for each user when it is not set
    cr.execute(
        """
        WITH first_stage AS (
            SELECT (array_agg(id ORDER BY sequence))[1] as stage_id, user_id
              FROM project_task_type
             WHERE user_id IS NOT NULL
          GROUP BY user_id
        )
        UPDATE project_task_user_rel as rel
           SET stage_id = s.stage_id
          FROM first_stage s
         WHERE s.user_id = rel.user_id
           AND rel.stage_id IS NULL
        """
    )

    # B. task - tags
    cr.execute(
        """
        INSERT INTO project_tags_project_task_rel (project_tags_id, project_task_id)
             SELECT tag.id, task.id
               FROM note_tags_rel AS rel
         INNER JOIN project_tags AS tag
                 ON rel.tag_id = tag._upg_note_tag_id
               JOIN project_task AS task
                 ON task._upg_note_id=rel.note_id
              WHERE tag._upg_note_tag_id IS NOT NULL
        """
    )

    # ----------- 6. Update references to notes models -----------------

    # A. Update references to project.task.type model
    cr.execute(
        """
        SELECT _upg_note_stage_id, id
          FROM project_task_type
         WHERE _upg_note_stage_id IS NOT NULL
        """
    )
    stage_id_mapping = dict(cr.fetchall())
    if stage_id_mapping:
        util.replace_record_references_batch(cr, stage_id_mapping, "note.stage", "project.task.type")

    # B. Update references to project.task model
    cr.execute(
        """
        SELECT _upg_note_id, id
          FROM project_task
         WHERE _upg_note_id IS NOT NULL
        """
    )
    note_id_mapping = dict(cr.fetchall())
    if note_id_mapping:
        util.replace_record_references_batch(cr, note_id_mapping, "note.note", "project.task")

    # ------------- 7. Add new tag to converted notes ------------------

    cr.execute(
        """
        INSERT INTO project_tags (name, color)
             VALUES ('{"en_US": "Converted Note"}', 1)
          RETURNING id
        """
    )
    converted_note_tag_id = cr.fetchone()[0]
    cr.execute(
        """
        INSERT INTO project_tags_project_task_rel (project_tags_id, project_task_id)
             SELECT %s, task.id
               FROM project_task AS task
              WHERE task._upg_note_id IS NOT NULL
        """,
        [converted_note_tag_id],
    )

    # Manually deleting unused xmlids
    util.delete_unused(
        cr,
        "project_todo.note_stage_00",
        "project_todo.note_stage_01",
        "project_todo.note_stage_02",
        "project_todo.note_stage_03",
    )
