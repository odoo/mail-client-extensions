# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_usage(cr, "crm.lead", "assign_date", "date_open")
    util.remove_field(cr, "crm.lead", "assign_date")
    util.remove_field(cr, "crm.team", "ratio")
    util.remove_field(cr, "crm.team", "leads_count")
    util.rename_field(cr, "crm.team", "capacity", "lead_capacity")

    util.remove_field(cr, "team.user", "percentage_leads")
    util.rename_field(cr, "team.user", "leads_count", "lead_month_count")

    util.rename_field(cr, "website.crm.score", "leads_count", "lead_all_count")
