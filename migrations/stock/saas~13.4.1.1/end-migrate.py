# -*- coding: utf-8 -*-
from collections import namedtuple

from odoo.upgrade import util


def clean_recursive_rules(env):
    # unraveling odoo/odoo/blob/9a4e792c38124e1c3902b37ea4604a17788c7710/addons/stock/models/product.py#L551
    def get_recursive_rules(product, location, route_ids=False, seen_rules=False):
        if not seen_rules:
            seen_rules = env["stock.rule"]
        rule = env["procurement.group"]._get_rule(
            product, location, {"route_ids": route_ids, "warehouse_id": location.get_warehouse()}
        )
        if not rule:
            return False
        if rule in seen_rules:
            return rule
        if rule.procure_method == "make_to_stock" or rule.action not in ("pull_push", "pull"):
            return False
        else:
            return get_recursive_rules(product, rule.location_src_id, seen_rules=(seen_rules | rule))

    RuleInfo = namedtuple("RuleInfo", "rid desc pid pname")
    info = []
    env.cr.execute("SELECT id FROM stock_warehouse_orderpoint")
    ids = [x[0] for x in env.cr.fetchall()]
    for orderpoint in util.iter_browse(env["stock.warehouse.orderpoint"], ids):
        product = orderpoint.product_id
        location = orderpoint.location_id
        if not product or not location:
            continue
        rule = get_recursive_rules(product, location, orderpoint.route_id)
        if rule:
            info.append(RuleInfo(rule.id, rule.rule_message, product.id, product.name))
            rule.active = False

    if not info:
        return

    # report the changes to the user
    util.add_to_migration_reports(
        f"""
        <details>
        <summary>
        Cyclic reordering rules were disabled during the upgrade. If you still need them please check and fix them
        manually.
        </summary>
        <h4>Disabled rules:</h4>
        <ul>
        {"".join(f"<li>Rule(id={r.rid}) for Product(id={r.pid}, name={r.pname}):<br/>{r.desc}</li>" for r in info)}
        </ul>
        </details>
        """,
        "Stock",
        format="html",
    )


def migrate(cr, version):
    env = util.env(cr)
    try:
        util.recompute_fields(cr, "stock.warehouse.orderpoint", ["qty_to_order"])
    except RecursionError:
        env.clear()  # must do this since the ORM left things half-baked from the exception above
        clean_recursive_rules(env)
        util.recompute_fields(cr, "stock.warehouse.orderpoint", ["qty_to_order"])

    env["stock.warehouse"]._check_multiwarehouse_group()
