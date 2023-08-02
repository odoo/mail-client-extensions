# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    """
    Update new column: slide_channel_partner.survey_certification_success
    """
    query = """
        WITH certification_success_slides AS (
            SELECT partner_id, channel_id
              FROM slide_slide_partner
             WHERE survey_scoring_success = True
               AND channel_id IS NOT NULL
          GROUP BY partner_id, channel_id
        )
        UPDATE slide_channel_partner AS scp
           SET survey_certification_success = True
          FROM certification_success_slides
         WHERE scp.partner_id = certification_success_slides.partner_id
           AND scp.channel_id = certification_success_slides.channel_id
    """
    util.explode_execute(cr, query, table="slide_channel_partner", alias="scp")
