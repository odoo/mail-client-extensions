from odoo import models

try:
    from odoo.addons.hr_recruitment.models import hr_applicant_category  # noqa
except ImportError:
    # < saas~16.1
    from odoo.addons.hr_recruitment.models import hr_recruitment  # noqa


def migrate(cr, version):
    pass


class HrApplicantCategory(models.Model):
    _inherit = ["hr.applicant.category"]
    _module = "hr_recruitment"
    _match_uniq = True
