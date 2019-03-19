# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "hr.appraisal", "mail_template_id", "survey_template_id")
    util.remove_field(cr, "hr.employee", "periodic_appraisal")
    util.remove_field(cr, "hr.employee", "appraisal_frequency")
    util.remove_field(cr, "hr.employee", "appraisal_frequency_unit")
