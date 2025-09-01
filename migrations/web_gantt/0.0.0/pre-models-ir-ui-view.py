from odoo import models

from odoo.addons.base.maintenance.migrations import util

if util.version_gte("saas~13.3"):
    from odoo.addons.web_gantt.models import ir_ui_view  # noqa


def migrate(cr, version):
    pass


class IrUiView(models.Model):
    _inherit = "ir.ui.view"
    _module = "web_gantt"

    if util.version_gte("saas~13.3"):

        def _validate_tag_gantt(self, *args, **kwargs):
            if self.env.context.get("_upgrade_custom_modules"):
                return None
            return super()._validate_tag_gantt(*args, **kwargs)
