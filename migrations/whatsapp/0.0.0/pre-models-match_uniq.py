from odoo import models

from odoo.addons.whatsapp.models import whatsapp_template  # noqa: F401


def migrate(cr, version):
    pass


class WhatsAppTemplate(models.Model):
    _inherit = "whatsapp.template"
    _module = "whatsapp"
    _match_uniq = True
