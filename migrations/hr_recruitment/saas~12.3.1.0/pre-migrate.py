# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_recruitment.{crm_case_form_view_job,hr_applicant_view_form}"))

    util.update_record_from_xml(cr, "hr_recruitment.group_hr_recruitment_user", reset_write_metadata=False)
    util.update_record_from_xml(cr, "hr_recruitment.group_hr_recruitment_manager", reset_write_metadata=False)
