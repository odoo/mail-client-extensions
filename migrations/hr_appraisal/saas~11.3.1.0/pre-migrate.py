# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "hr_appraisal.mt_appraisal_new")
    util.remove_record(cr, "hr_appraisal.mt_appraisal_meeting")
    util.remove_record(cr, "hr_appraisal.mt_appraisal_sent")
