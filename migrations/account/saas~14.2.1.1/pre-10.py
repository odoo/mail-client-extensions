# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # ===============================================================
    # Removal of the inherits in account_tour_upload_bill (PR:59169)
    # ===============================================================
    util.remove_inherit_from_model(cr, "account.tour.upload.bill", "mail.compose.message")
    util.remove_field(cr, "account.tour.upload.bill", "composer_id")
