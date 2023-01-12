# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_model(cr, "mail.mass_mailing", "mailing.mailing")
    util.rename_model(cr, "mail.mass_mailing.contact", "mailing.contact")
    util.rename_model(cr, "mail.mass_mailing.list", "mailing.list")
    # update m2m fields
    cr.execute("ALTER TABLE mail_mass_mailing_list_rel RENAME COLUMN mail_mass_mailing_id TO mailing_mailing_id")
    cr.execute("ALTER TABLE mail_mass_mailing_list_rel RENAME COLUMN mail_mass_mailing_list_id TO mailing_list_id")
    cr.execute(
        """
        ALTER TABLE mail_mass_mailing_contact_res_partner_category_rel
          RENAME TO mailing_contact_res_partner_category_rel;
        ALTER TABLE mailing_contact_res_partner_category_rel
      RENAME COLUMN mail_mass_mailing_contact_id TO mailing_contact_id
    """
    )

    util.rename_model(cr, "mail.mass_mailing.list_contact_rel", "mailing.contact.subscription")
    util.rename_model(cr, "mail.mail.statistics", "mailing.trace")

    cr.execute("DROP VIEW IF EXISTS mail_statistics_report")
    util.rename_model(cr, "mail.statistics.report", "mailing.trace.report", rename_table=False)

    util.rename_model(cr, "mass.mailing.list.merge", "mailing.list.merge")
    cr.execute("DROP TABLE mail_mass_mailing_list_mass_mailing_list_merge_rel")
    util.rename_model(cr, "mass.mailing.schedule.date", "mailing.mailing.schedule.date")
    util.rename_model(cr, "mail.mass_mailing.test", "mailing.mailing.test")

    util.rename_field(cr, "link.tracker.click", "mail_stat_id", "mailing_trace_id")
    util.rename_field(cr, "mail.mail", "statistics_ids", "mailing_trace_ids")
    util.rename_field(cr, "mailing.mailing", "statistics_ids", "mailing_trace_ids")

    util.create_column(cr, "mailing_mailing", "mailing_type", "varchar")
    util.create_column(cr, "mailing_mailing", "unique_ab_testing", "boolean")
    cr.execute("UPDATE mailing_mailing SET mailing_type='mail'")
    cr.execute(
        """
        UPDATE mailing_mailing m
           SET unique_ab_testing = c.unique_ab_testing
          FROM mail_mass_mailing_campaign c
         WHERE c.id = m.mass_mailing_campaign_id
    """
    )

    for model in {"link.tracker", "link.tracker.click", "mailing.mailing", "mailing.trace", "mail.compose.message"}:
        util.remove_field(cr, model, "mass_mailing_campaign_id")

    util.remove_field(cr, "mailing.contact.subscription", "contact_count")
    util.remove_field(cr, "mailing.contact", "is_email_valid")
    util.rename_field(cr, "mailing.list", "subscription_contact_ids", "subscription_ids")

    util.create_column(cr, "mailing_trace", "failure_type", "varchar")
    util.create_column(cr, "mailing_trace", "trace_type", "varchar")
    util.create_column(cr, "mailing_trace", "campaign_id", "int4")

    if True:
        util.parallel_execute(
            cr,
            util.explode_query(
                cr,
                """
                    UPDATE mailing_trace
                       SET failure_type = 'UNKNOWN'
                     WHERE state = 'exception'
                       AND failure_type IS NULL
                """,
            )
            + util.explode_query(
                cr,
                """
                    UPDATE mailing_trace
                       SET failure_type = 'BOUNCE'
                     WHERE state = 'bounced'
                       AND failure_type IS NULL
                """,
            ),
        )
        util.parallel_execute(
            cr, util.explode_query(cr, "UPDATE mailing_trace SET trace_type='mail' WHERE trace_type IS NULL")
        )

        util.parallel_execute(
            cr,
            util.explode_query(
                cr,
                """
                    UPDATE mailing_trace mt
                       SET campaign_id = mm.campaign_id
                      FROM mailing_mailing mm
                     WHERE mm.id=mt.mass_mailing_id
                       AND mt.campaign_id IS NULL
                       AND {parallel_filter}
                """,
                alias="mt",
            ),
        )

    util.remove_model(cr, "mail.mass_mailing.campaign")

    # remove m2m to transient model
    cr.execute("DROP TABLE mail_compose_message_mail_mass_mailing_list_rel")
