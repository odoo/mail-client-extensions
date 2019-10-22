# -*- coding: utf-8 -*-
import logging

from odoo.tools.safe_eval import safe_eval
import odoo.osv.expression as exp

from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.base.saas12-4."
_logger = logging.getLogger(NS + __name__)

evaluation_context = {"user": util.SelfPrint("user"), "time": util.SelfPrint("time")}


def migrate(cr, version):
    cr.execute(r"SELECT id, domain_force FROM ir_rule WHERE domain_force ~ '\yuser\.company_id\.id\y'")
    for rid, domain in util.log_progress(cr.fetchall(), "ir.rule"):
        try:
            eval_dom = safe_eval(domain, evaluation_context)
        except Exception:
            _logger.warning("Cannot evaluate rule #%s: %r", rid, domain, exc_info=True)
            continue
        final_dom = []
        for element in eval_dom:
            if not exp.is_leaf(element):
                final_dom.append(element)
                continue

            left, operator, right = element = exp.normalize_leaf(element)
            if operator == "child_of" and repr(right) == "[user.company_id.id]":
                final_dom.append((left, "in", util.SelfPrint("company_ids")))
            else:
                final_dom.append(element)
        _logger.debug("#%s: %r -> %r", rid, domain, final_dom)
        cr.execute("UPDATE ir_rule SET domain_force = %s WHERE id = %s", [str(final_dom), rid])
