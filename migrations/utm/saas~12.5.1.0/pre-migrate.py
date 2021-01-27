# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "mail_mass_mailing_stage"):
        util.rename_model(cr, "mail.mass_mailing.stage", "utm.stage")
        util.move_model(cr, "utm.stage", "mass_mailing", "utm")

        util.rename_model(cr, "mail.mass_mailing.tag", "utm.tag")
        util.move_model(cr, "utm.tag", "mass_mailing", "utm")
    else:
        # For some obscure reasons of a mandatory field, not creating the table make the migration fail
        cr.execute(
            """
        CREATE TABLE utm_stage (
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            name varchar,
            sequence int4
        )
        """
        )

    util.create_column(cr, "utm_campaign", "user_id", "int4")
    util.create_column(cr, "utm_campaign", "stage_id", "int4")
    util.create_column(cr, "utm_campaign", "is_website", "boolean")
    util.create_column(cr, "utm_campaign", "color", "int4")

    if util.column_exists(cr, "mail_mass_mailing_campaign", "campaign_id"):
        cr.execute(
            """
            UPDATE utm_campaign u
               SET user_id = m.user_id,
                   stage_id = m.stage_id,
                   color = m.color
              FROM mail_mass_mailing_campaign m
             WHERE u.id = m.campaign_id
        """
        )
        # Both m2m (old and new) have been wrongly defined and fields swapped.
        # campaign_id REFERENCES utm_tag(id)
        # tag_id REFERENCES utm_campaign(id)
        # Marvelous!
        util.create_m2m(cr, "utm_tag_rel", "utm_campaign", "utm_tag", "tag_id", "campaign_id")
        cr.execute(
            """
            INSERT INTO utm_tag_rel(campaign_id, tag_id)
                 SELECT r.campaign_id, c.campaign_id
                   FROM mail_mass_mailing_tag_rel r
                   JOIN mail_mass_mailing_campaign c ON (c.id = r.tag_id)
        """
        )
    cr.execute(
        """
        UPDATE utm_campaign
           SET user_id = COALESCE(create_uid, write_uid)
         WHERE user_id IS NULL
    """
    )

    eb = util.expand_braces
    for i in {1, 2, 3}:
        util.rename_xmlid(cr, *eb("{mass_mailing,utm}.campaign_stage_%s" % i))

    util.rename_xmlid(cr, "mass_mailing.mass_mail_tag_1", "utm.utm_tag_1")
