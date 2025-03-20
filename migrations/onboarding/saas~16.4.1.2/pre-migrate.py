# old-style import because this script is imported for tests
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # progress.steps are now linked to company_id and not to the onboarding.progress, see below.
    util.remove_constraint(cr, "onboarding_progress_step", "onboarding_progress_step_progress_step_uniq")

    # onboarding_step -> onboarding is now many2many
    util.create_m2m(
        cr,
        "onboarding_onboarding_onboarding_onboarding_step_rel",
        "onboarding_onboarding",
        "onboarding_onboarding_step",
    )
    cr.execute(
        """
       INSERT INTO onboarding_onboarding_onboarding_onboarding_step_rel(onboarding_onboarding_id, onboarding_onboarding_step_id)
            SELECT onboarding_id, id
              FROM onboarding_onboarding_step
        """
    )

    # onboarding_progress_step -> onboarding_progress is now many2many
    util.create_m2m(
        cr, "onboarding_progress_onboarding_progress_step_rel", "onboarding_progress", "onboarding_progress_step"
    )
    util.create_column(cr, "onboarding_progress_step", "company_id", "int4")
    util.create_column(cr, "onboarding_onboarding_step", "is_per_company", "boolean")
    cr.execute(
        """
        UPDATE onboarding_onboarding_step step
           SET is_per_company = panel.is_per_company
          FROM onboarding_onboarding panel
         WHERE step.onboarding_id = panel.id
        """
    )
    cr.execute(
        """
       UPDATE onboarding_progress_step
          SET company_id = onboarding_progress.company_id
         FROM onboarding_progress
        WHERE onboarding_progress_step.progress_id = onboarding_progress.id
        """
    )
    cr.execute(
        """
       INSERT INTO onboarding_progress_onboarding_progress_step_rel(onboarding_progress_id, onboarding_progress_step_id)
            SELECT progress_id, id
              FROM onboarding_progress_step
        """
    )

    util.remove_field(cr, "onboarding.progress.step", "progress_id")
    util.remove_field(cr, "onboarding.progress.step", "onboarding_id")
    util.remove_column(cr, "onboarding_onboarding", "is_per_company")
    util.remove_field(cr, "onboarding.onboarding.step", "onboarding_id")


def migrate_onboarding(cr, onboarding_params: dict, remove_step_fields_for_module="ALL"):
    """
    Migrate onboardings from res.company to onboarding module records.
    This will also remove the onboarding and steps (unless other
    `remove_step_fields_for_module` value) state fields.
    Run in post-migrate to have onboarding data installed.
    :param cr:
    :param onboarding_params: A dictionary with entries:
        ```
        onboarding_alias: str: {
            "state_field": str  # name of the res.company field used before to track the onboarding,
            "id": str:          # ref for the matching onboarding.onboarding record,
            "steps": List[Tuple[
                str:            # name of the res.company field used before to tracking the step,
                str:            # ref for the onboarding.onboarding.step record
            ]]
        }
        ```
    :param remove_step_fields_for_module: bool: Set `False` to keep step all step state fields.
      See `remove_onboarding_step_state_fields`.
    """
    converted_onboarding_params = _convert_refs_to_ids(cr, onboarding_params)
    steps_data_query = _get_steps_data_query(converted_onboarding_params)

    # nosemgrep dont-execute-format-query
    cr.execute(
        """
        WITH steps_data AS (
            {steps_data_query}
        ),
        sum_done AS (
            SELECT s.company_id AS company_id,
                   s.onboarding_id AS onboarding_id,
                   CASE {onboarding_completion_rules}
                        ELSE 'not_done'
                   END onboarding_state,
                   CASE {onboarding_closed_rules}
                        ELSE FALSE
                   END is_onboarding_closed
              FROM steps_data s
              JOIN res_company c
                ON s.company_id = c.id
             WHERE s.step_state IN ('done', 'just_done')
          GROUP BY s.company_id, s.onboarding_id, {onboarding_state_fields}
        ),
        onboarding_progress_rows AS (
            INSERT INTO onboarding_progress (company_id, onboarding_id, onboarding_state, is_onboarding_closed)
                 SELECT company_id, onboarding_id, onboarding_state, is_onboarding_closed
                   FROM sum_done
              RETURNING *
        ),
        full_onboarding_data AS (
            SELECT onboarding_progress_rows.company_id c_id,
                   steps_data.step_id s_id,
                   steps_data.step_state s_state
              FROM steps_data
              JOIN onboarding_progress_rows
                ON steps_data.company_id = onboarding_progress_rows.company_id
               AND steps_data.onboarding_id = onboarding_progress_rows.onboarding_id
        ),
        existing_onboarding_progress_step_rows AS (
            SELECT ops.id AS id,
                   ops.company_id AS company_id,
                   ops.step_id AS step_id,
                   ops.step_state AS step_state
              FROM onboarding_progress_step ops
              JOIN full_onboarding_data fod
                ON fod.c_id = ops.company_id
               AND fod.s_id = ops.step_id
        ),
        new_onboarding_progress_step_rows AS (
            INSERT INTO onboarding_progress_step (company_id, step_id, step_state)
                 SELECT c_id, s_id, s_state
                   FROM full_onboarding_data
                 EXCEPT
                 SELECT company_id, step_id, step_state
                   FROM existing_onboarding_progress_step_rows
              RETURNING id, company_id, step_id
        ),
        onboarding_progress_step_rows AS (
            SELECT id, company_id, step_id
              FROM existing_onboarding_progress_step_rows
         UNION ALL
            SELECT id, company_id, step_id
              FROM new_onboarding_progress_step_rows
        ),
        progress_step_links AS (
            SELECT onboarding_progress_rows.id onboarding_progress_id,
                   onboarding_progress_step_rows.id onboarding_progress_step_id
              FROM onboarding_progress_rows
              JOIN onboarding_onboarding_onboarding_onboarding_step_rel onb_step_rel
                ON onboarding_progress_rows.onboarding_id = onb_step_rel.onboarding_onboarding_id
              JOIN onboarding_progress_step_rows
                ON onboarding_progress_step_rows.step_id = onb_step_rel.onboarding_onboarding_step_id
        )
        INSERT INTO onboarding_progress_onboarding_progress_step_rel (onboarding_progress_id, onboarding_progress_step_id)
             SELECT onboarding_progress_id, onboarding_progress_step_id
               FROM progress_step_links
    """.format(
            steps_data_query=steps_data_query,
            onboarding_completion_rules=_get_completion_rules(converted_onboarding_params),
            onboarding_closed_rules=_get_closed_rules(converted_onboarding_params),
            onboarding_state_fields=", ".join(
                f"c.{onboarding_data['state_field']}" for onboarding_data in converted_onboarding_params.values()
            ),
        )
    )

    if remove_step_fields_for_module:
        remove_onboarding_step_state_fields(cr, onboarding_params, remove_step_fields_for_module)

    _remove_onboarding_state_fields(cr, converted_onboarding_params)


def migrate_standalone_onboarding_steps(cr, onboarding_params: dict, remove_step_fields_for_module="ALL"):
    """
    Migrates onboardings steps from res.company to onboarding module records.
    Similar to `migrate_onboarding`, when steps to be moved are not linked to an onboarding
    (even if they are later linked to an onboarding panel, including in another module's migration)
    This will also remove the steps state fields, modify with `remove_step_fields_for_module`
    To be run in post-migrate to have onboarding data installed.
    For parameters, see migrate_onboarding.
    """
    converted_onboarding_params = _convert_refs_to_ids(cr, onboarding_params)
    steps_data_query = _get_steps_data_query(converted_onboarding_params)

    # nosemgrep dont-execute-format-query
    cr.execute(
        f"""
        WITH steps_data AS (
            {steps_data_query}
        )
        INSERT INTO onboarding_progress_step (company_id, step_id, step_state)
             SELECT company_id, step_id, step_state
               FROM steps_data
        """
    )

    if remove_step_fields_for_module:
        remove_onboarding_step_state_fields(cr, onboarding_params, remove_step_fields_for_module)


def remove_onboarding_step_state_fields(cr, onboarding_params, module_name="ALL"):
    """
    :param cr:
    :param onboarding_params: see `get_onboarding_migration_params`
    :param module_name: Only delete steps migrated to module_name module, or
      `"ALL"` to remove all steps
    """
    for field_name in (
        field_name
        for onboarding_data in onboarding_params.values()
        for field_name, step_id in onboarding_data["steps"]
        if module_name == "ALL" or step_id.startswith(f"{module_name}.")
    ):
        util.remove_field(cr, "res.company", field_name)


def _remove_onboarding_state_fields(cr, onboarding_params):
    for onboarding_data in onboarding_params.values():
        util.remove_field(cr, "res.company", onboarding_data["state_field"])


def _convert_refs_to_ids(cr, onboarding_params):
    return {
        onboarding_alias: {
            "state_field": onboarding_data["state_field"],
            "id": onboarding_data["id"] and util.ref(cr, onboarding_data["id"]),
            "steps": [
                (step_state_field, util.ref(cr, step_ref)) for step_state_field, step_ref in onboarding_data["steps"]
            ],
        }
        for onboarding_alias, onboarding_data in onboarding_params.items()
    }


def _get_steps_data_query(onboarding_params):
    return "UNION ALL".join(
        f"""
        SELECT id company_id,
               {onboarding_data["id"] or "NULL"} onboarding_id,
               {step_id} step_id,
               {
            field_name
            if field_name.endswith("state")
            else f"CASE WHEN {field_name} = TRUE THEN 'done' ELSE 'not_done' END"
        } step_state
          FROM res_company
        """
        for onboarding_data in onboarding_params.values()
        for field_name, step_id in onboarding_data["steps"]
    )


def _get_completion_rules(onboarding_params):
    return "".join(
        f"""
                        WHEN s.onboarding_id = {onboarding_data["id"]} THEN
                            CASE WHEN COUNT(*) = {len(onboarding_data["steps"])} THEN 'done' ELSE 'not_done' END
        """
        for onboarding_data in onboarding_params.values()
    )


def _get_closed_rules(onboarding_params):
    return "".join(
        f"""
                        WHEN s.onboarding_id = {onboarding_data["id"]} THEN
                            COUNT(*) = {len(onboarding_data["steps"])} OR c.{onboarding_data["state_field"]} = 'closed'
        """
        for onboarding_data in onboarding_params.values()
    )
