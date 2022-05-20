# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    old_user = util.ref(cr, "sale_subscription.group_sale_subscription_view")
    old_manager = util.ref(cr, "sale_subscription.group_sale_subscription_manager")
    new_user = util.ref(cr, "sales_team.group_sale_salesman")
    new_manager = util.ref(cr, "sales_team.group_sale_manager")

    util.replace_record_references_batch(
        cr, {old_user: new_user, old_manager: new_manager}, "res.groups", replace_xmlid=False
    )

    util.remove_record(cr, "sale_subscription.group_sale_subscription_view")
    util.remove_record(cr, "sale_subscription.group_sale_subscription_manager")
