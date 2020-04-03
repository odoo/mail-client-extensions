# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "hr.employee", "appraisal_date", "last_appraisal_date")
    util.rename_field(cr, "res.users", "appraisal_date", "last_appraisal_date")
    util.create_column(cr, "hr_employee", "next_appraisal_date", "date")

    util.remove_field(cr, "hr.employee", "appraisal_date_related")
    util.remove_field(cr, "hr.employee", "appraisal_count")

    util.create_column(cr, "hr_departure_wizard", "cancel_appraisal", "boolean")
