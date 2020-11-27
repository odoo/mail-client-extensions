import os
from odoo.tools.misc import str2bool
from odoo.addons.base.maintenance.migrations.testing import IntegrityCase


class TestModuleState(IntegrityCase):
    def invariant(self):
        # Checking the module state is only relevant in controlled environments,
        # when we know that all the modules should be upgraded.
        if str2bool(os.getenv("MATT", "0")):
            self.env.cr.execute("SELECT name, state FROM ir_module_module WHERE state LIKE 'to %'")
            return dict(self.env.cr.fetchall())
        return {}
