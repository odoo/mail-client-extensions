# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_model(cr, "crm.lead.tag", "crm", "sales_team", move_data=True)
    if util.table_exists(cr, "crm_lead_tag"):  # `crm` not necessary installed
        util.rename_model(cr, "crm.lead.tag", "crm.tag")

    renames = """
        access_crm{_lead,}_tag
        access_crm{_lead,}_tag_salesman
        access_crm{_lead,}_tag_manager

        {crm_lead_tag_form,sales_team_crm_tag_view_form}
        {crm_lead_tag_tree,sales_team_crm_tag_view_tree}
        {crm_lead_tag_action,sales_team_crm_tag_action}
    """
    for rename in util.splitlines(renames):
        old, new = util.expand_braces(rename)
        util.rename_xmlid(cr, f"sales_team.{old}", f"sales_team.{new}")
