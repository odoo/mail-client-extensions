# -*- coding: utf-8 -*-
import os

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    When a module is added in stable it may look like the module has been removed from the next version point of view.
    Runbot will add some information in the environment to indicate that a new module is being forwardported.
    This scripts automaticaly remove the module if it is found in the environment and not in the addons path.
    """

    exceptions = os.environ.get("suppress_upgrade_warnings", "").split(",")
    for exception in exceptions:
        if exception.startswith("module:"):
            module, _, version = exception[7:].partition(":")
            if version and not util.version_gte(version):
                continue
            if not util.get_manifest(module):
                cr.execute("SELECT true FROM ir_module_module WHERE name = %s", [module])
                if bool(cr.fetchone()):
                    util._logger.log(
                        util.NEARLYWARN, "New module %r explicitly ignored and automaticaly removed", module
                    )
                    util.remove_module(cr, module)
