# -*- coding: utf-8 -*-
import logging

from odoo.tools.safe_eval import safe_eval
import odoo.osv.expression as exp

from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.base.saas12-5."
_logger = logging.getLogger(NS + __name__)

# NOTE: reuse util.IndirectReference, but store domain field in `res_id`
# TODO move it to util?
IR = util.IndirectReference
domain_fields = [
    IR("ir_model_fields", "model", "domain"),
    IR("ir_act_window", "res_model", "domain"),
    IR("ir_filters", "model_id", "domain"),
    IR("ir_rule", None, "force_domain", "domain_id"),
    IR("mail_mass_mailing", None, "mailing_domain", "mailing_model_id"),
    IR("mailing_mailing", None, "mailing_domain", "mailing_model_id"),
    # TODO dupe with `base_action_rule`
    IR("base_automation", "(SELECT model_name FROM ir_act_server WHERE id = t.action_server_id)", "filter_domain"),
    IR("base_automation", "(SELECT model_name FROM ir_act_server WHERE id = t.action_server_id)", "filter_pre_domain"),
    # destination model is always "res.users"
    IR("gamification_challenge", "'res.users'", "user_domain"),
    IR("gamification_goal_definition", None, "domain", "model_id"),
    IR("marketing_campaign", "model_name", "domain"),
    IR("marketing_activity", "(SELECT model_name FROM marketing_campaign WHERE id = t.campaign_id)", "domain"),
    IR("marketing_activity", "(SELECT model_name FROM marketing_campaign WHERE id = t.campaign_id)", "activity_domain"),
    IR("sale_subscription_template", "'sale.subscription'", "good_health_domain"),
    IR("sale_subscription_template", "'sale.subscription'", "bad_health_domain"),
]

evaluation_context = {
    "uid": util.SelfPrint("uid"),
    "user": util.SelfPrint("user"),
    "time": util.SelfPrint("time"),
    "website": util.SelfPrint("website"),
}


def valid_path_to(cr, path, from_, to):
    model = from_
    while path:
        field = path.pop(0)
        cr.execute(
            """
            SELECT relation
              FROM ir_model_fields
             WHERE model = %s
               AND name = %s
        """,
            [model, field],
        )
        if not cr.rowcount:
            # unknown field. Maybe an old domain. Cannot validate it.
            return False
        [model] = cr.fetchone()

    return model == to


def adapt(cr, model, domain):
    try:
        eval_dom = safe_eval(domain, evaluation_context)
    except Exception:
        _logger.warning("Cannot evaluate %r domain: %r", model, domain, exc_info=True)
        return None

    final_dom = []
    changed = False
    for element in eval_dom:
        if not exp.is_leaf(element):
            final_dom.append(element)
            continue

        left, operator, right = exp.normalize_leaf(element)

        path = left.split(".")
        if path[-1] in {"customer", "supplier"} and valid_path_to(cr, path[:-1], model, "res.partner"):
            # verify that path of left point to a res.partner
            left += "_rank"
            thruthy_op = "=" if bool(right) else "!="
            operator = ">" if operator == thruthy_op else "="
            right = 0
            changed = True

        final_dom.append((left, operator, right))

    if not changed:
        return None

    _logger.debug("%s: %r -> %r", model, domain, final_dom)
    return str(final_dom)


def adapt_domains(cr, model):
    for ir in domain_fields:
        if not util.column_exists(cr, ir.table, ir.res_id):
            continue

        model_select = ir.res_model
        if not model_select:
            model_select = f"(SELECT model FROM ir_model m WHERE m.id = t.{ir.res_model_id})"

        cr.execute(
            fr"""
            SELECT id, {model_select}, {ir.res_id}
              FROM {ir.table} t
             WHERE (   {ir.res_id} ~ '\ycustomer\y'
                    OR {ir.res_id} ~ '\ysupplier\y'
                   )
        """
        )
        for id_, model, domain in cr.fetchall():
            domain = adapt(cr, model, domain)
            if domain:
                cr.execute(f"UPDATE {ir.table} SET {ir.res_id} = %s WHERE id = %s", [domain, id_])


def migrate(cr, version):
    util.remove_field(cr, "res.partner", "customer", drop_column=False)
    util.remove_field(cr, "res.partner", "supplier", drop_column=False)

    # Now adapt domains...
    # FIXME what to do if `account` is not installed?
    adapt_domains(cr, "res.partner")
    util.update_field_references(cr, "customer", "customer_rank", only_models=("res.partner",))
    util.update_field_references(cr, "supplier", "supplier_rank", only_models=("res.partner",))
