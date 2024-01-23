# -*- coding: utf-8 -*-
import logging

from odoo import models

from odoo.addons.base.maintenance.migrations import util

try:
    from odoo.addons.base.models import res_users as _ignore
except ImportError:
    # version 10
    from odoo.addons.base.res import res_users as _ignore  # noqa


_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base." + __name__)


def migrate(cr, version):
    pass


class Groups(models.Model):
    _inherit = "res.groups"
    _module = "base"

    def write(self, values):
        implied_ids = values.get("implied_ids")
        if not implied_ids or any(cmd[0] not in [3, 4, 5, 6] for cmd in implied_ids):
            return super(Groups, self).write(values)

        values = dict(values)
        values.pop("implied_ids")
        to_write = self.browse()
        for group in self:
            ids = set(group.implied_ids.ids)
            for cmd in implied_ids:
                if cmd[0] == 3:
                    ids.discard(cmd[1])
                elif cmd[0] == 4:
                    ids.add(cmd[1])
                elif cmd[0] == 5:
                    ids = set()
                elif cmd[0] == 6:
                    ids = set(cmd[2])

            if ids != set(group.implied_ids.ids):
                super(Groups, group).write(dict(values, implied_ids=[(6, 0, ids)]))
            else:
                _logger.log(
                    util.NEARLYWARN,
                    "skip writing implied_ids=%r on %r as it won't change its value",
                    implied_ids,
                    group,
                )
                to_write |= group
        if to_write:
            super(Groups, to_write).write(values)
        return True
