from odoo import models

from odoo.addons.hr_recruitment.models import hr_recruitment  # noqa


def migrate(cr, version):
    pass


class HrApplicantCategory(models.Model):
    _inherit = "hr.applicant.category"
    _module = "hr_recruitment"
    _match_uniq = True
