# -*- coding: utf-8 -*-
from odoo import models

import odoo.addons.hr_work_entry.models.hr_work_entry as _ignored  # noqa


def migrate(cr, version):
    pass


class WorkEntryType(models.Model):
    _name = "hr.work.entry.type"
    _inherit = ["hr.work.entry.type"]
    _module = "hr_work_entry"
    _match_uniq = True
