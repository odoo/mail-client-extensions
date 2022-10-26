# -*- coding: utf-8 -*-

from ast import literal_eval

from odoo.osv import expression

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT id,name,bad_health_domain,good_health_domain
          FROM sale_order_template
        WHERE bad_health_domain != '[]'
           OR good_health_domain != '[]'
        """
    )
    env = util.env(cr)
    alert_create_vals = []
    for template_id, name, bad_domain, good_domain in cr.fetchall():
        if bad_domain != "[]":
            alert_create_vals.append(
                {
                    "name": "Bad health upgraded domain for template %s %s" % (name, template_id),
                    "subscription_template_ids": [(6, 0, [template_id])],
                    "trigger_condition": "on_create_or_write",
                    "action": "set_health_value",
                    "health": "bad",
                    "filter_domain": expression.AND(
                        [literal_eval(bad_domain), [("sale_order_template_id", "=", template_id)]]
                    ),
                }
            )
        if good_domain != "[]":
            alert_create_vals.append(
                {
                    "name": "Good health upgraded domain for template %s %s" % (name, template_id),
                    "subscription_template_ids": [(6, 0, [template_id])],
                    "trigger_condition": "on_create_or_write",
                    "action": "set_health_value",
                    "health": "done",
                    "filter_domain": expression.AND(
                        [literal_eval(good_domain), [("sale_order_template_id", "=", template_id)]]
                    ),
                }
            )
    env["sale.order.alert"].create(alert_create_vals)

    util.remove_field(cr, "sale.order.template", "bad_health_domain")
    util.remove_field(cr, "sale.order.template", "good_health_domain")
