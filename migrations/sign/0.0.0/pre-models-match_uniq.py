from odoo import models

from odoo.addons.sign.models import sign_template  # noqa


def migrate(cr, version):
    pass


class Tags(models.Model):
    _name = "sign.template.tag"
    _inherit = ["sign.template.tag"]
    _module = "sign"
    _match_uniq = True
