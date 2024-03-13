from odoo import models

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pass


if util.version_gte("saas~17.3"):

    class IrActions(models.Model):
        _inherit = "ir.actions.actions"
        _module = "base"

        def write(self, vals):
            if "path" in vals and self.path and self.path != vals["path"]:
                util._logger.warning(
                    "Skip modifying action (id=%s, name=%s) path from %r to %r, to avoid breaking existing urls",
                    self.id,
                    self.name,
                    self.path,
                    vals["path"],
                )
                vals.pop("path")
            return super().write(vals)
