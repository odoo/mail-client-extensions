# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # We compute the hours separately because we do not
    # want to let the days be recomputed.
    cr.execute("SELECT id FROM hr_leave")
    ids = [lid for (lid,) in cr.fetchall()]
    Leave = util.env(cr)["hr.leave"].with_context(mail_notrack=True)
    for leave in util.iter_browse(Leave, ids):
        _, hours = leave._get_duration()
        leave.number_of_hours = hours
