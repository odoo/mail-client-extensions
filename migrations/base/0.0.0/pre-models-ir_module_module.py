# -*- coding: utf-8 -*-
from odoo import models

try:
    from odoo.addons.base.models import ir_module as _ignore  # noqa
except ImportError:
    # version 10
    from odoo.addons.base.module import module as _ignore  # noqa

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pass


class Module(models.Model):
    _inherit = "ir.module.module"
    _module = "base"

    def create(self, values):
        if not values:
            # Great! The `_load_records` method can call us with an empty list...
            return self.browse()
        modules = [v["name"] for v in values] if isinstance(values, list) else [values["name"]]
        modules = [m for m in modules if "test" not in m]
        if modules:
            raise util.MigrationError("New modules %r should be declared via an upgrade script." % (modules,))

        # else create the test modules
        return super(Module, self).create(values)

    def _update_dependencies(self, depends=None, *args, **kwargs):
        if "test" in self.name:
            return super(Module, self)._update_dependencies(depends, *args, **kwargs)

        existing = set(dep.name for dep in self.dependencies_id)
        needed = set(depends or [])
        if needed != existing:
            plus = needed - existing
            minus = existing - needed
            diff = "\n".join(["\n".join(" + %s" % p for p in plus), "\n".join(" - %s" % m for m in minus)])
            raise util.MigrationError(
                "Changes of the %r module dependencies should be handled via an upgrade script.\n%s" % (self.name, diff)
            )
