from odoo import models

from odoo.addons.mail.models import mail_alias  # noqa


def migrate(cr, version):
    pass


class Alias(models.Model):
    _name = "mail.alias"
    _inherit = ["mail.alias"]
    _module = "mail"

    def _alias_is_ascii(self):
        pass
