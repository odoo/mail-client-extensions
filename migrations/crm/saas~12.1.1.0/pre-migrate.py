# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_gte("saas~12.5"):
        util.remove_field(cr, "crm.team", "use_leads")
    util.remove_field(cr, "crm.team", "dashboard_graph_period_pipeline")
    util.remove_field(cr, "crm.team", "dashboard_graph_group_pipeline")

    util.create_column(cr, 'crm_team', 'alias_user_id', 'int4')
    cr.execute("""
        UPDATE crm_team t
           SET alias_user_id=a.alias_user_id
          FROM mail_alias a
         WHERE t.alias_id=a.id
    """)
    #mail.address.mixin
    util.create_column(cr, "crm_lead", "email_normalized", "varchar")
    cr.execute("""
        UPDATE crm_lead
           SET email_normalized=lower(substring(email_from, '([^ ,;<@]+@[^> ,;]+)'))
         WHERE email_from IS NOT NULL
    """)
    util.remove_field(cr, "crm.lead", "partner_address_mobile")
