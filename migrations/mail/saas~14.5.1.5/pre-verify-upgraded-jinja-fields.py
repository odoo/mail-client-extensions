# -*- coding: utf-8 -*-
from odoo import api, models

from odoo.upgrade.util.jinja_to_qweb import verify_upgraded_jinja_fields


def migrate(cr, version):
    pass


class MailTemplate(models.Model):
    _inherit = "mail.template"
    _module = "mail"

    @api.model
    def _register_hook(self):
        verify_upgraded_jinja_fields(self.env.cr)
        return super()._register_hook()
