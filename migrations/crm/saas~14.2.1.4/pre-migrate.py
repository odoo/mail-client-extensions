# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    # remove global alias configuration
    util.remove_field(cr, "res.config.settings", "crm_alias_prefix")
    util.remove_field(cr, "res.config.settings", "generate_lead_from_alias")
    # remove alias xml ID but keep data as it may be used; only configuration is removed
    cr.execute(
        """
            DELETE
              FROM ir_model_data
             WHERE module = 'crm'
               AND name = 'mail_alias_lead_info'
        """
    )

    util.rename_xmlid(cr, "crm.crm_team_salesteams_view_kanban", "crm.crm_team_view_kanban_dashboard")
    util.rename_xmlid(cr, *eb("crm.ir_cron{,_crm}_lead_assign"))

    util.rename_field(cr, "crm.team.member", "maximum_user_leads", "assignment_max")
    util.rename_field(cr, "crm.team.member", "team_user_domain", "assignment_domain")
    util.create_column(cr, "crm_team_member", "assignment_max", "int4", default=30)
    util.create_column(cr, "crm_team_member", "assignment_domain", "varchar")

    util.rename_field(cr, "crm.team", "score_team_domain", "assignment_domain")
    util.rename_field(cr, "crm.team", "lead_capacity", "assignment_max")
    util.remove_field(cr, "crm.team", "min_for_assign")
    util.create_column(cr, "crm_team", "assignment_optout", "boolean")
    util.create_column(cr, "crm_team", "assignment_domain", "varchar")

    util.create_column(cr, "res_config_settings", "crm_use_auto_assignment", "boolean")
    util.create_column(cr, "res_config_settings", "crm_auto_assignment_interval_type", "varchar")
    util.create_column(cr, "res_config_settings", "crm_auto_assignment_interval_number", "int4")
    util.create_column(cr, "res_config_settings", "crm_auto_assignment_run_datetime", "timestamp without time zone")

    util.remove_model(cr, "website.crm.score")

    # Replace field usage in at least order of filters
    cr.execute(
        r"""
            UPDATE ir_filters
               SET sort = regexp_replace(sort, '\mscore\M', 'probability')
             WHERE model_id = 'crm.lead'
               AND sort ilike '%score%'

        """
    )
    # TODO util.adapt_domains(cr, "crm.lead", "score", "probability", adapter=lamdba op, val: op, val * 0.15)

    util.remove_field(cr, "crm.lead", "score")
    util.remove_field(cr, "crm.lead", "score_ids")

    for view in [
        "crm_opportunity_view_dashboard",
        "crm_lead_view_dashboard",
        "lead_tree_view",
        "lead_score_form",
        "score_opp_tree_view",
        "sales_team_form_view_assign",
    ]:
        util.remove_view(cr, f"crm.{view}")

    util.remove_menus(cr, [util.ref(cr, "crm.team_user")])
