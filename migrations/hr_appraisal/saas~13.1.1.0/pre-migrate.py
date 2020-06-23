# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.appraisal", "collaborators_appraisal")
    util.remove_field(cr, "hr.appraisal", "colleagues_appraisal")
    util.remove_field(cr, "hr.appraisal", "employee_appraisal")

    util.remove_field(cr, "request.appraisal", "recipient_id")
