import logging
import os

from odoo import models

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base." + __name__)


def migrate(cr, version):
    pass


if util.version_gte("saas~16.4"):
    from odoo.addons.base.models.ir_ui_menu import IrUiMenu as _ignore  # noqa

    class Menu(models.Model):
        _name = "ir.ui.menu"
        _inherit = ["ir.ui.menu"]
        _module = "base"

        def unlink(self):
            to_ignore = os.getenv("suppress_upgrade_warnings", "").split(",")  # noqa: SIM112
            for menu in self:
                if menu.parent_id:
                    continue
                xmlid = menu.get_metadata()[0]["xmlid"]
                if not xmlid:
                    continue
                if "xmlid:{}".format(xmlid) in to_ignore:
                    _logger.log(util.NEARLYWARN, "menu unlink %s explicitly ignored", xmlid)
                else:
                    _logger.critical('It looks like you forgot to call `util.remove_record(cr, "%s")`', xmlid)

            return super().unlink()
