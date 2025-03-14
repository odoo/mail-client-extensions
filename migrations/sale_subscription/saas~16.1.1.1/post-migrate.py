from ast import literal_eval

from odoo.osv import expression

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    alert_create_vals = []

    if util.version_gte("saas~16.5"):
        query = """
              WITH plan_agg AS (
                SELECT template_id,
                       ARRAY_AGG(id) AS plan_ids
                  FROM sale_subscription_plan
              GROUP BY template_id
              )

            SELECT plan_ids,
                   name,
                   company_id,
                   bad_health_domain,
                   good_health_domain
              FROM sale_order_template
              JOIN plan_agg ON plan_agg.template_id = sale_order_template.id
             WHERE bad_health_domain != '[]'
                OR good_health_domain != '[]'
            """
        f_name_alert = "subscription_plan_ids"
        f_name_so = "plan_id"
    else:
        query = """
            SELECT array[id],name,company_id,bad_health_domain,good_health_domain
              FROM sale_order_template
            WHERE bad_health_domain != '[]'
               OR good_health_domain != '[]'
            """
        f_name_alert = "subscription_template_ids"
        f_name_so = "sale_order_template_id"

    cr.execute(query)
    for plan_template_ids, name, company_id, bad_domain, good_domain in cr.fetchall():
        if bad_domain != "[]":
            alert_create_vals.append(
                {
                    "name": "Bad health upgraded domain for plan(s) %s %s" % (name, plan_template_ids),
                    "company_id": company_id,
                    f_name_alert: [(6, 0, plan_template_ids)],
                    "trigger_condition": "on_create_or_write",
                    "action": "set_health_value",
                    "health": "bad",
                    "filter_domain": expression.AND([literal_eval(bad_domain), [(f_name_so, "in", plan_template_ids)]]),
                }
            )
        if good_domain != "[]":
            alert_create_vals.append(
                {
                    "name": "Good health upgraded domain for plan(s) %s %s" % (name, plan_template_ids),
                    "company_id": company_id,
                    f_name_alert: [(6, 0, plan_template_ids)],
                    "trigger_condition": "on_create_or_write",
                    "action": "set_health_value",
                    "health": "done",
                    "filter_domain": expression.AND(
                        [literal_eval(good_domain), [(f_name_so, "in", plan_template_ids)]]
                    ),
                }
            )

    env["sale.order.alert"].create(alert_create_vals)

    util.remove_field(cr, "sale.order.template", "bad_health_domain")
    util.remove_field(cr, "sale.order.template", "good_health_domain")
