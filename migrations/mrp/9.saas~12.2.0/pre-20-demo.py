# -*- coding: utf-8 -*-
from odoo import models
from odoo.addons.base.maintenance.migrations import util
from odoo.addons.mrp.wizard import mrp_product_produce as _ignore  # noqa


def migrate(cr, version):
    tmpl_id = util.ref(cr, "product.product_product_27_product_template")
    if tmpl_id:
        cr.execute("UPDATE product_template SET tracking='lot' WHERE id = %s", [tmpl_id])


class MPP(models.TransientModel):
    _inherit = "mrp.product.produce"
    _module = "mrp"

    def do_produce(self):
        # For I-spent-too-much-time-on-this-issue reasons, demo data are not in a upgradable state.
        # This method is called by the yaml file updating one new demo record.
        # As this is done during the data loading part, we cannot adapt it in a `post-` script.
        # This should not interfere with customer data.
        # This is only do to make matt happy.
        self.consume_line_ids.write({"lot_id": self.lot_id.id})
        return super(MPP, self).do_produce()
