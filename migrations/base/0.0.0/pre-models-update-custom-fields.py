from odoo import models

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pass


class Base(models.AbstractModel):
    _inherit = "base"
    _module = "base"

    if util.version_gte("16.0"):

        def _auto_init(self):
            super(Base, self.with_context(update_custom_fields=True))._auto_init()
