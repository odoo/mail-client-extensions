# -*- coding: utf-8 -*-
import logging

from odoo import models

try:
    from odoo.addons.base.models import ir_module as _ignore
except ImportError:
    # version 10
    from odoo.addons.base.module import module as _ignore  # noqa

try:
    from odoo.modules import get_modules
except ImportError:
    pass

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.util.inconsistencies import break_recursive_loops

_logger = logging.getLogger("odoo.upgrade.base.ir_module_module")


def migrate(cr, version):
    if not util.version_gte("15.0"):
        return
    break_recursive_loops(cr, "ir.module.category", "parent_id")


class Module(models.Model):
    _name = "ir.module.module"
    _inherit = ["ir.module.module"]
    _module = "base"

    def create(self, values):
        if not values:
            # Great! The `_load_records` method can call us with an empty list...
            return self.browse()
        modules = [v["name"] for v in values] if isinstance(values, list) else [values["name"]]
        modules = [m for m in modules if "test" not in m]
        if modules:
            if util.version_gte("15.0"):
                code_modules = set(get_modules())
                data_modules = [m for m in modules if m not in code_modules]
                if data_modules:
                    _logger.log(
                        logging.CRITICAL if util.on_CI() else logging.WARNING,
                        "The modules %r are not in the addons path, "
                        "maybe there is wrong data in the base/data/ir_module_module.xml file.",
                        data_modules,
                    )
            else:
                _logger.log(
                    logging.CRITICAL if util.on_CI() else logging.WARNING,
                    "New modules %r must be declared via an upgrade script via `util.new_module`.",
                    modules,
                )

        # else create the test modules
        return super(Module, self).create(values)

    def _update_dependencies(self, depends=None, *args, **kwargs):
        if "test" in self.name:
            return super(Module, self)._update_dependencies(depends, *args, **kwargs)

        existing = {dep.name for dep in self.dependencies_id}
        needed = set(depends or [])
        if needed != existing:
            plus = needed - existing
            minus = existing - needed
            diff = "\n".join(["\n".join(" + " + p for p in plus), "\n".join(" - " + m for m in minus)])
            _logger.log(
                logging.CRITICAL if util.on_CI() else logging.WARNING,
                "Changes of the %r module dependencies should be handled via an upgrade script. Diff:\n%s",
                self.name,
                diff,
            )
        return None
