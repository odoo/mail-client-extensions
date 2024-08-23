# -*- coding: utf-8 -*-
import logging

from odoo import models

try:
    from odoo.addons.base.models import ir_module as _ignore
except ImportError:
    # version 10
    from odoo.addons.base.module import module as _ignore  # noqa

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.upgrade.base.ir_module_module")


def migrate(cr, version):
    if not util.version_gte("15.0"):
        return
    cr.execute(
        """
        WITH RECURSIVE info AS (
         SELECT array[id] AS path,
                False AS cycle
           FROM ir_module_category
          WHERE parent_id IS NOT NULL

          UNION ALL

         SELECT child.parent_id || curr.path AS path,
                child.parent_id = any(curr.path) AS cycle
           FROM info AS curr
           JOIN ir_module_category AS child
             ON child.id = curr.path[1]
          WHERE child.parent_id IS NOT NULL
            AND NOT curr.cycle
         )
         SELECT path FROM info WHERE cycle
        """,
    )
    if not cr.rowcount:
        return
    ids = []
    done = set()
    for (cycle,) in cr.fetchall():
        to_break = min(cycle[: cycle.index(cycle[0], 1)])
        if to_break not in done:
            ids.append(to_break)
        done.update(cycle)
    cr.execute(
        """
        UPDATE ir_module_category
           SET parent_id = NULL
         WHERE id IN %s
     RETURNING id, name
        """,
        [tuple(ids)],
    )
    _logger.warning(
        "The module categories %s were found to be recursive, their `parent_id` were set to NULL",
        ", ".join("{!r} (id={})".format(name, id_) for id_, name in cr.fetchall()),
    )


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
            _logger.log(
                util.NEARLYWARN,
                r"New modules %r should be declared via an upgrade script. But do what you want ¯\_(ツ)_/¯.",
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
                util.NEARLYWARN,
                "Changes of the %r module dependencies should be handled via an upgrade script. "
                "But do what you want ¯\\_(ツ)_/¯. Diff:\n%s",
                self.name,
                diff,
            )
        return None
