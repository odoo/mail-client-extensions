# -*- coding: utf-8 -*-
from odoo import api, models

from odoo.addons.mail.models.mail_message import Message  # noqa

from odoo.upgrade.util.jinja_to_qweb import verify_upgraded_jinja_fields


def migrate(cr, version):
    pass


class MailMessage(models.Model):
    # overwrite `mail.message` to ensure we are called *before* the rendering of the upgrade report
    _inherit = "mail.message"
    _module = "mail"

    @api.model
    def _register_hook(self):
        verify_upgraded_jinja_fields(self.env.cr)
        return super()._register_hook()
