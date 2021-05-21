# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "mail_mass_mailing_campaign", "campaign_id", "int4")

    # have to be done in 2 query. Update of utm_campaign.name cannot be done in the CTE as it does
    # not have knowledge of just inserted rows we try updating
    cr.execute(
        """
        WITH s AS (SELECT id FROM mail_mass_mailing_campaign WHERE campaign_id IS NULL),
             i AS (INSERT INTO utm_campaign(name) SELECT id::varchar FROM s RETURNING id, name),
             u AS (UPDATE mail_mass_mailing_campaign c
                      SET campaign_id = i.id
                     FROM i
                    WHERE c.id = i.name::int4)
      SELECT id FROM i
    """
    )
    cids = [c[0] for c in cr.fetchall()]
    cr.execute(
        """UPDATE utm_campaign u
                     SET name = m.name
                    FROM mail_mass_mailing_campaign m
                   WHERE u.id = m.campaign_id
                     AND u.id = ANY(%s)
               """,
        [cids],
    )


if __name__ == "__main__":
    util.main(migrate)
