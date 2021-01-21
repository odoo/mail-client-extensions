# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.move_model(cr, "team.user", "crm", "sales_team")
    # as this model come from the now defunct module `website_crm_score`, the table may not exists
    util.rename_model(cr, "team.user", "crm.team.member", rename_table=util.table_exists(cr, "team_user"))
    util.rename_field(cr, "crm.team.member", "team_id", "crm_team_id")

    util.move_field_to_module(cr, "res.users", "team_user_ids", "crm", "sales_team")
    util.rename_field(cr, "res.users", "team_user_ids", "crm_team_member_ids")

    util.move_field_to_module(cr, "crm.team", "team_user_ids", "crm", "sales_team")
    util.rename_field(cr, "crm.team", "team_user_ids", "crm_team_member_ids")

    renames = """
        # crm.team
        sales_team.crm_team_salesteams_act              sales_team.crm_team_action_sales
        sales_team.crm_team_salesteams_pipelines_act    sales_team.crm_team_action_pipeline
        sales_team.sales_team_config_action             sales_team.crm_team_action_config
        sales_team.crm_team_salesteams_search           sales_team.crm_team_view_search
        sales_team.crm_team_salesteams_view_kanban      sales_team.crm_team_view_kanban_dashboard

        # crm.team.member
        crm.team_user_view_search       sales_team.crm_team_member_view_search
        crm.view_crm_team_user_tree     sales_team.crm_team_member_view_tree
        crm.view_crm_team_user_form     sales_team.crm_team_member_view_form
        crm.team_user_kanban            sales_team.crm_team_member_view_kanban
        crm.team_user_action            sales_team.crm_team_member_action
    """
    for change in util.splitlines(renames):
        util.rename_xmlid(cr, *change.split())

    # if we did not have website_crm_score installed: create new m2m table and
    # update it with currently stored information
    if not util.table_exists(cr, "crm_team_member"):
        cr.execute(
            """
            CREATE TABLE crm_team_member (
                crm_team_id integer NOT NULL REFERENCES crm_team(id) ON DELETE CASCADE,
                user_id integer NOT NULL REFERENCES res_users(id) ON DELETE CASCADE,
                id serial NOT NULL PRIMARY KEY,
                create_uid integer,
                create_date timestamp without time zone,
                write_uid integer,
                write_date timestamp without time zone,
                active boolean
            );
            CREATE INDEX ON crm_team_member(user_id, crm_team_id);
        """
        )

        # migrate existing relationship (m2o user.sale_team_id) into m2m
        cr.execute(
            """
            INSERT INTO crm_team_member (crm_team_id, user_id, active)
                 SELECT sale_team_id, id, true
                   FROM res_users
                  WHERE sale_team_id IS NOT NULL
        """
        )
    else:
        # keep only a single living user / team membership
        cr.execute(
            """
            WITH membership AS (
                SELECT user_id, crm_team_id, unnest((array_agg(id ORDER BY id DESC))[2:]) as mid
                  FROM crm_team_member
              GROUP BY user_id, crm_team_id
                HAVING count(*) > 1
            )
            UPDATE crm_team_member
               SET active = false
              FROM membership
             WHERE crm_team_member.id = membership.mid;
        """
        )

    # avoid issues with admin due to sales_team data crm_team_member_admin_sales
    # that makes admin member of team_sales_department. We should not try to create
    # it twice as a constraint will raise.
    util.ensure_xmlid_match_record(
        cr,
        "sales_team.crm_team_member_admin_sales",
        "crm.team.member",
        {
            "user_id": util.ref(cr, "base.user_admin"),
            "crm_team_id": util.ref(cr, "sales_team.team_sales_department"),
        },
    )
    user_demo, team_demo = util.ref(cr, "base.user_demo"), util.ref(cr, "sales_team.crm_team_1")
    if user_demo and team_demo:
        util.ensure_xmlid_match_record(
            cr,
            "sales_team.crm_team_member_demo_team_1",
            "crm.team.member",
            {
                "user_id": user_demo,
                "crm_team_id": team_demo,
            },
        )
