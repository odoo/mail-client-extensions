# -*- coding: utf-8 -*-
try:
    from odoo import Command
except ImportError:
    # `Command` is only available in recent versions
    Command = None

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class TestMigrateProviders(UpgradeCase):
    def prepare(self):
        if util.version_gte("saas~16.2"):
            model = "payment.method"
            field = "payment_method_ids"
        else:
            model = "payment.icon"
            field = "payment_icon_ids"

        dummy_method = self.env[model].create({"name": "dummy"})
        dummy_method2 = self.env[model].create({"name": "dummy2"})

        # Add custom pm to the base provider.
        authorize = self.env.ref("payment.payment_provider_authorize")
        authorize[field] = [Command.link(dummy_method.id)]

        # Create a duplicate provider with different payment methods.
        duplicate = authorize.copy({field: [Command.set([dummy_method2.id])]})
        return {"duplicate": duplicate.id}

    def check(self, data):
        provider_authorize = self.env.ref("payment.payment_provider_authorize")
        duplicate = self.env["payment.provider"].browse(data["duplicate"])
        provider_stripe = self.env.ref("payment.payment_provider_stripe")

        # Check that pms are updated and are the same for the provider and its duplicate.
        self.assertEqual(
            provider_authorize.with_context(active_test=False).payment_method_ids.ids,
            duplicate.with_context(active_test=False).payment_method_ids.ids,
        )

        # Check that unsupported pms are removed.
        self.assertFalse(
            self.env["payment.method"].with_context(active_test=False).search([("name", "in", ("dummy", "dummy2"))])
        )

        # Check that uninstalled providers (with the code 'none') have different pms
        self.assertNotEqual(
            provider_authorize.with_context(active_test=False).payment_method_ids.ids,
            provider_stripe.with_context(active_test=False).payment_method_ids.ids,
        )
