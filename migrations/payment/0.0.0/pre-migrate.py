# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util

if util.version_gte("saas~16.5"):
    import logging

    from odoo import exceptions, models

    from odoo.addons.payment.models import payment_provider  # noqa

    _logger = logging.getLogger("odoo.addons.base.maintenance.migrations.payment.0.0.0." + __name__)

    class PaymentProvider(models.Model):
        _inherit = ["payment.provider"]
        _name = "payment.provider"
        _module = "payment"

        def _check_required_if_provider(self):
            try:
                super()._check_required_if_provider()
            except exceptions.ValidationError as e:
                _logger.warning("Invalid payment providers %s: %s", self.mapped("name"), e.args[0])


def migrate(cr, version):
    if util.version_between("17.0", "18.0"):
        util.delete_unused(cr, "payment.payment_method_acss_debit")

    if util.version_between("saas~11.4", "19.0"):
        util.change_field_selection_values(
            cr,
            "payment.transaction",
            "state",
            {
                "refunding": "pending",
                "refunded": "done",
            },
        )
