# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # populate ab_testing_winner_mailing_id field as it now determines ab_testing_completed
    util.create_column(cr, "utm_campaign", "ab_testing_winner_mailing_id", "int4")
    cr.execute(
        """UPDATE utm_campaign campaign
      SET ab_testing_winner_mailing_id = mailing.id
     FROM mailing_mailing mailing
    WHERE campaign.id = mailing.campaign_id
      AND mailing.ab_testing_pc = 100;
       """
    )

    util.remove_field(cr, "utm.campaign", "ab_testing_total_pc")
    util.remove_column(cr, "mailing_mailing", "ab_testing_completed")  # unstored related.
