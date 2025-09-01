# -*- coding: utf-8 -*-
from odoo import models

from odoo.addons.base_vat.models import res_partner  # noqa


def migrate(cr, version):
    pass


# A method from the base_vat module is overridden here because it needs this definition during
# upgrade to avoid crashes, even if the base_vat module is installed during the upgrade process
# If the base_vat module is not installed, defining this method during the upgrade is harmless
class ResPartner(models.Model):
    _inherit = "res.partner"
    _module = "base_vat"

    # Completely skip VAT check during upgrade
    def check_vat(self):
        pass
