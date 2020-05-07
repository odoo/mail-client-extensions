# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
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
