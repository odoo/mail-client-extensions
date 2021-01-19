# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "mass_mailing.mass_mailing_kpi_link_trackers", False)

    # remove date schedule wizard
    util.remove_model(cr, "mailing.mailing.schedule.date")
    util.remove_view(cr, "mass_mailing.mailing_mailing_schedule_date_view_form")
    util.remove_record(cr, "mass_mailing.mailing_mailing_schedule_date_action")

    # support calendar view
    util.create_column(cr, "mailing_mailing", "schedule_type", "varchar", default="now")
    util.create_column(cr, "mailing_mailing", "calendar_date", "timestamp without time zone")

    cr.execute(
        """
        UPDATE mailing_mailing
           SET schedule_type='scheduled'
         WHERE schedule_date IS NOT NULL"""
    )
    cr.execute(
        """
            WITH cron AS (
                SELECT c.nextcall
                  FROM ir_cron c
                  JOIN ir_model_data d ON d.model = 'ir.cron' AND d.res_id = c.id
                  WHERE d.module = 'mass_mailing'
                    AND d.name = 'ir_cron_mass_mailing_queue'
            )
            UPDATE mailing_mailing
               SET calendar_date = CASE state WHEN 'done' THEN sent_date
                                              WHEN 'in_queue' THEN GREATEST(schedule_date, cron.nextcall)
                                              WHEN 'sending' THEN write_date  -- most accurate value than `now()` used by code
                                    END
              FROM cron
             WHERE state IN ('done', 'in_queue', 'sending')
               AND calendar_date IS NULL
        """
    )

    util.rename_field(cr, "mailing.list", "contact_nbr", "contact_count")
