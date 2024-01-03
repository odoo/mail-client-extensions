# -*- coding: utf-8 -*-

import os

from odoo.upgrade import util


def migrate(cr, version):
    # We compute the hours separately because we do not
    # want to let the days be recomputed.
    compute_leave_hours = os.getenv("UPG_COMPUTE_LEAVE_HOURS", "all")
    if compute_leave_hours == "skip":
        return
    query = "SELECT id FROM hr_leave"
    if compute_leave_hours == "current_year":
        query += " WHERE extract(YEAR FROM date_to) >= extract(YEAR FROM current_date)"
    cr.execute(query)
    ids = [lid for (lid,) in cr.fetchall()]
    Leave = util.env(cr)["hr.leave"].with_context(mail_notrack=True)
    for leave in util.iter_browse(Leave, ids):
        _, hours = leave._get_duration()
        leave.number_of_hours = hours
