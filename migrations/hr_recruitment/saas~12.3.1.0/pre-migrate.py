# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_recruitment.{crm_case_form_view_job,hr_applicant_view_form}"))
