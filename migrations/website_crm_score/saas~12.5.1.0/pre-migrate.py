# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "team_user", "team_id", "int4")

    util.rename_field(cr, "team.user", "running", "active")
    util.rename_field(cr, "website.crm.score", "running", "active")

    cr.execute(
        """
        UPDATE team_user tu
        SET team_id=p.team_id
        FROM res_users u
        INNER JOIN res_partner p ON u.partner_id=p.id
        WHERE tu.user_id=u.id
          AND tu.team_id IS NULL
          AND p.team_id IS NOT NULL
        """
    )
    cr.execute(
        """
        ALTER TABLE crm_lead_scoring_frequency_field
    DROP CONSTRAINT crm_lead_scoring_frequency_field_field_id_fkey,
     ADD CONSTRAINT crm_lead_scoring_frequency_field_field_id_fkey
        FOREIGN KEY (field_id)
         REFERENCES ir_model_fields(id) ON DELETE CASCADE
        """
    )
    util.remove_field(cr, "crm.lead", "score_pageview_ids")
    util.remove_field(cr, "crm.lead", "pageviews_count")
    util.remove_field(cr, "crm.lead", "lang_id")
    util.remove_field(cr, "crm.lead", "phone")

    util.remove_model(cr, "website.crm.pageview")
