# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.users", "google_cal_account_id", "google_calendar_account_id")
