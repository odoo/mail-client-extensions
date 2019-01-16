# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "group_website_multiimage")
    util.remove_record(cr, "website_sale.group_website_multi_image")

    util.remove_view(cr, "website_sale.continue_shopping")
    util.remove_view(cr, "website_sale.bill_to")

    # pre-update views without verification
    util.update_record_from_xml(cr, "website_sale.wizard_checkout")
    util.update_record_from_xml(cr, "website_sale.extra_info_option")
