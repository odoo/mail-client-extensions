# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "helpdesk_team", "website_form_view_id", "int4")

    util.remove_view(cr, "website_helpdesk_form.ticket_submit")

    # https://github.com/odoo/enterprise/blob/be1ab29ba1f1aecb7370dfdd19ae7f4156c3b4d2/helpdesk/models/helpdesk.py#L180
    MODULE_FIELD = {
        "website_helpdesk_form": "use_website_helpdesk_form",
        "website_helpdesk_livechat": "use_website_helpdesk_livechat",
        "website_helpdesk_forum": "use_website_helpdesk_forum",
        "website_helpdesk_slides": "use_website_helpdesk_slides",
        "helpdesk_timesheet": "use_helpdesk_timesheet",
        "helpdesk_sale_timesheet": "use_helpdesk_sale_timesheet",
        "helpdesk_account": "use_credit_notes",
        "helpdesk_stock": "use_product_returns",
        "helpdesk_repair": "use_product_repairs",
        "helpdesk_sale_coupon": "use_coupons",
    }

    cr.execute(
        "SELECT name FROM ir_module_module WHERE state = 'uninstalled' AND name = any(%s)",
        [list(MODULE_FIELD)],
    )

    fields_to_update = [MODULE_FIELD[module] for module, in cr.fetchall()]
    if fields_to_update:
        cr.execute(
            "UPDATE helpdesk_team SET {}".format(", ".join("{} = False".format(field) for field in fields_to_update))
        )
