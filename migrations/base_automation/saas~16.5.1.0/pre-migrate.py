# -*- coding: utf-8 -*-


from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "base_automation", "name", "jsonb")
    util.create_column(cr, "base_automation", "model_id", "integer", fk_table="ir_model", on_delete_action="CASCADE")
    util.create_column(cr, "base_automation", "model_name", "varchar")
    cr.execute(
        """
            WITH data AS (
               SELECT ba.id,
                      ba.action_server_id,
                      ba.trigger,
                      act.name,
                      act.model_id,
                      act.model_name,
                      CASE ba.trigger
                      WHEN 'on_create' THEN false -- deprecated trigger should be deactivated
                      WHEN 'on_write'  THEN false -- deprecated trigger should be deactivated
                      ELSE ba.active
                      END AS active
                 FROM base_automation AS ba
                      LEFT JOIN ir_act_server AS act
                      ON act.id = ba.action_server_id
            )
               UPDATE base_automation
                  SET name = data.name::jsonb,
                      model_id = data.model_id,
                      model_name = data.model_name,
                      active = data.active
                 FROM data
                WHERE base_automation.id = data.id
            RETURNING data.*
        """
    )
    results = cr.dictfetchall()
    util.add_to_migration_reports(
        """
            <details>
            <summary>
                Automated actions are now automation rules supporting multiple actions.
                <br/>
                Some triggers have also been deprecated: <code>On Creation</code>, <code>On Update</code>.
                If you had any automated actions using these triggers, you will see them in the list right below.
                They have been converted but they are archived (and thus deactivated).
                You will need to manually adapt them.
                You may try to use the new <code>On Save</code> trigger instead.
                This new trigger corresponds to the previous `On Creation and Update` trigger.
                So you need to make sure you set the proper triggering fields and conditions.
            </summary>
            <ul>%s</ul>
            </details>
        """
        % (
            "\n".join(
                "<li>The converted automation rule %s has a deprecated trigger and has been archived.</li>"
                % (util.get_anchor_link_to_record("base.automation", automation["id"], automation["name"]["en_US"]),)
                for automation in filter(lambda a: a["trigger"] in ["on_create", "on_write"], results)
            ),
        ),
        "Automation Rules",
        format="html",
    )

    util.create_column(cr, "ir_act_server", "base_automation_id", "integer")
    cr.execute(
        """
            UPDATE ir_act_server
               SET base_automation_id = ba.id
              FROM base_automation AS ba
             WHERE ir_act_server.id = ba.action_server_id
        """
    )
    # Note: child_ids  cannot be removed along with the inheritance below
    # because we are touching base models that have indirect references.
    # If included in the removal, the inheritance removal method would try to
    # delete the link between server actions and automation rules  (as in,
    # it would try to delete server actions that run on automation rules),
    # which is incorrect (and would crash because of a FKEY violation on ir_cron)
    util.remove_inherit_from_model(
        cr,
        "base.automation",
        "ir.actions.server",
        keep=(
            "name",
            "model_id",
            "model_name",
            "child_ids",
        ),
    )

    util.remove_field(cr, "base.automation", "action_server_id")
    util.remove_field(cr, "base.automation", "child_ids")

    # actually still there, but should be force-refresh as it is now
    # a complete view instead of an extension of server action form view
    util.remove_view(cr, "base_automation.view_base_automation_form")
