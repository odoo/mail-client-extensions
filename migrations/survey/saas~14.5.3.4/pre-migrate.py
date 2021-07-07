# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "survey_user_input", "end_datetime", "timestamp without time zone")

    cr.execute(
        """
        UPDATE survey_user_input
           SET end_datetime = write_date
         WHERE state = 'done'
        """
    )
