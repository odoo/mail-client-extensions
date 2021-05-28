# -*- coding: utf-8 -*-
import logging

import odoo.osv.expression as exp
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.base.saas12-4."
_logger = logging.getLogger(NS + __name__)

evaluation_context = {
    "user": util.SelfPrint("user"),
    "time": util.SelfPrint("time"),
    "website": util.SelfPrint("website"),
}


def adapt(domain, qualifier):
    try:
        eval_dom = safe_eval(domain, evaluation_context)
    except Exception:
        _logger.warning("Cannot evaluate %s: %r", qualifier, domain, exc_info=True)
        return None

    final_dom = []
    for element in eval_dom:
        if not exp.is_leaf(element):
            final_dom.append(element)
            continue

        left, operator, right = element = exp.normalize_leaf(element)
        if (operator == "child_of" and repr(right) == "[user.company_id.id]") or (
            operator == "=" and repr(right) == "user.company_id.id"
        ):
            final_dom.append((left, "in", util.SelfPrint("company_ids")))
        else:
            final_dom.append(element)
    _logger.debug("%s: %r -> %r", qualifier, domain, final_dom)
    return str(final_dom)


def migrate(cr, version):
    cr.execute(r"SELECT id, domain_force FROM ir_rule WHERE domain_force ~ '\yuser\.company_id\.id\y'")
    for rid, domain in util.log_progress(cr.fetchall(), _logger, "ir.rule"):
        final_dom = adapt(domain, f"rule#{rid}")
        if final_dom:
            cr.execute("UPDATE ir_rule SET domain_force = %s WHERE id = %s", [final_dom, rid])

    cr.execute(r"SELECT id, domain FROM ir_filters WHERE domain ~ '\yuser\.company_id\.id\y'")
    for rid, domain in util.log_progress(cr.fetchall(), _logger, "ir.filters"):
        final_dom = adapt(domain, f"filter#{rid}")
        if final_dom:
            cr.execute("UPDATE ir_filters SET domain = %s WHERE id = %s", [final_dom, rid])
