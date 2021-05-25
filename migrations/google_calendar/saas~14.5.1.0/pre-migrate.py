# -*- coding:utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    """
    google_calendar move google credentials (tokens) from res_users to a dedicated table
    """
    util.create_column(cr, "res_users", "google_cal_account_id", "int4")
