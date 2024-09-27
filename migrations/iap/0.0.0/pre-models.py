from odoo.addons.base.maintenance.migrations import util

if util.version_gte("saas~17.5"):
    from odoo import models

    from odoo.addons.iap.models import iap_service as _ignore  # noqa: F401

    class IapService(models.Model):
        _inherit = ["iap.service"]
        _module = "iap"
        _match_uniq = True


def migrate(cr, version):
    pass
