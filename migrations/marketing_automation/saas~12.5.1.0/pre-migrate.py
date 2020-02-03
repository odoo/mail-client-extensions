# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "marketing_activity", "mass_mailing_id_mailing_type", "varchar")
    util.rename_field(cr, "marketing.trace", "mail_statistics_ids", "mailing_trace_ids")
    util.remove_view(cr, "marketing_automation.mail_mail_statistics_view_form")
    util.remove_view(cr, "marketing_automation.mailing_trace_view_form")

    cr.execute(
        """
            UPDATE marketing_campaign mc
            SET domain = REPLACE(mc.domain, 'stage_id.probability', 'probability')
            FROM ir_model im
            WHERE
                mc.model_id = im.id AND
                im.model = 'crm.lead' AND
                mc.domain like '%stage_id.probability%'
        """
    )
