# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Make (partner_id, channel_id) unique in slide_channel_partner. Keep the
    # one with highest channel completion if conflicts.
    cr.execute(
        """
        WITH scp_ranked AS (
            SELECT id AS scp_id,
                   ROW_NUMBER() OVER (
                        PARTITION BY channel_id, partner_id
                            ORDER BY completion DESC, write_date DESC
                                  ) scp_rank
            FROM slide_channel_partner
        )
      DELETE
        FROM slide_channel_partner scp
       USING scp_ranked
       WHERE scp.id = scp_ranked.scp_id
         AND scp_ranked.scp_rank > 1
        """
    )

    # Make (partner_id, slide_id) unique in slide_slide_partner. Order by
    # certificate succeeded (if possible), then complete, then update
    order = "completed DESC, write_date DESC"
    if util.module_installed(cr, "website_slides_survey"):
        order = "survey_scoring_success DESC, %s" % order

    cr.execute(
        """
        WITH ssp_ranked AS (
            SELECT id AS ssp_id,
                   ROW_NUMBER() OVER (
                        PARTITION BY slide_id, partner_id
                            ORDER BY %s
                                  ) scp_rank
            FROM slide_slide_partner
        )
      DELETE
        FROM slide_slide_partner ssp
       USING ssp_ranked
       WHERE ssp.id = ssp_ranked.ssp_id
         AND ssp_ranked.scp_rank > 1
        """
        % order
    )

    # Clean completion values (0 - 100 boundaries)
    cr.execute("UPDATE slide_channel_partner SET completion = 0 WHERE completion IS NULL")
    cr.execute(
        """
        UPDATE slide_channel_partner
           SET completion = GREATEST(LEAST(completion, 100), 0)
         WHERE completion NOT BETWEEN 0 AND 100
        """
    )

    # Limit vote value by sql constraint to -1, 0 or 1
    cr.execute(
        """
        UPDATE slide_slide_partner
           SET vote = COALESCE(SIGN(vote), 0)
         WHERE vote NOT IN (-1, 0, 1) OR vote IS NULL
        """
    )

    # Link URLs have been updated in the following templates
    util.update_record_from_xml(cr, "website_slides.slide_template_published")
    util.update_record_from_xml(cr, "website_slides.slide_template_shared")

    # Unused views
    util.remove_view(cr, "website_slides.rating_rating_view_search_slides")
