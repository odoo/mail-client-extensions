# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "hr.applicant", "residence_country")
    util.remove_view(cr, "website_hr_recruitment.view_hr_applicant_form_inherit_website")
