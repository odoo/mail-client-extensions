from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import IntegrityCase


class TestModuleState(IntegrityCase):
    def invariant(self):
        # Checking the module state is only relevant in controlled environments,
        # when we know that all the modules should be upgraded.
        if util.on_CI():
            self.env.cr.execute("SELECT name, state FROM ir_module_module WHERE state LIKE 'to %'")
            return dict(self.env.cr.fetchall())
        return {}
