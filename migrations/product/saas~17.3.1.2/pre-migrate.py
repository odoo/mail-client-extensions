from functools import partial

from odoo.osv import expression

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(cr, "product_attribute_value", "product_attribute_value_value_company_uniq")

    if util.module_installed(cr, "stock"):

        def adapter_product(leaf, _or, _neg):
            # Adapt the selection value 'product' in `product.template.type` and `product.template.detailed_type
            # into `is_storable` boolean field. Since not all leaves need to be adapted
            # we need to replace the left path manually.
            left, op, right = leaf
            path = left.split(".")
            path[-1] = "is_storable"
            new_left = ".".join(path)
            if right == "product" and op in ("=", "!="):
                return [(new_left, "=", op == "=")]
            elif right == "consu" and op == "=":
                return ["&", leaf, (new_left, "=", False)]
            elif right == "consu" and op == "!=":
                return ["|", leaf, "&", (left, "=", right), (new_left, "=", True)]
            elif isinstance(right, (tuple, list)) and "product" in right and op in ("in", "not in"):
                new_right = list(right)
                new_right.remove("product")
                if not new_right:
                    return [(new_left, "=", op == "in")]
                return ["|" if op == "in" else "&", (new_left, "=", op == "in"), (left, op, new_right)]
            elif isinstance(right, (tuple, list)) and "consu" in right and op in ("in", "not in"):
                return ["&" if op == "in" else "|", (new_left, "=", op == "not in"), leaf]
            return [(left, op, right)]

        util.adapt_domains(cr, "product.template", "detailed_type", "detailed_type", adapter=adapter_product)
        util.adapt_domains(cr, "product.template", "type", "type", adapter=adapter_product)

    if util.module_installed(cr, "appointment_account_payment"):

        def adapter_booking_fees(leaf, _or, _neg):
            # Adapt the selection value 'booking_fees' in `product.template.type` and `product.template.detailed_type`
            left, op, right = leaf
            path = "".join(left.rpartition(".")[0:2])
            fees_dom = ["&", (f"{path}type", "=", "service"), (f"{path}sale_ok", "=", True)]
            if op not in ["=", "in"]:
                fees_dom.insert(0, "!")
            if op in ("=", "!=", "in", "not in") and (
                right == "booking_fees" or (isinstance(right, (tuple, list)) and "booking_fees" in right)
            ):
                type_dom = expression.FALSE_DOMAIN
                if isinstance(right, (tuple, list)):
                    new_right = list(right)
                    new_right.remove("booking_fees")
                    if new_right:
                        type_dom = [(left, op, new_right)]
                        if "service" in new_right:
                            # when service is in new_right we don't need to add fees domain since all booking_fees are services
                            return type_dom
                return expression.OR([type_dom, fees_dom])
            return [leaf]

        util.adapt_domains(cr, "product.template", "detailed_type", "detailed_type", adapter=adapter_booking_fees)

    def adapter(leaf, _or, _neg, sel):
        # Adapt given selection value 'sel' in `product.template.type` and `product.template.detailed_type`
        # into `service_tracking` field.# into `service_tracking` field.
        # the aim is to replace different types e.g `event_booth` by
        # type=service and service_tracking=event_booth
        left, op, right = leaf
        if op in ("=", "!=", "in", "not in") and (right == sel or (isinstance(right, (tuple, list)) and sel in right)):
            type_dom = expression.FALSE_DOMAIN
            if isinstance(right, (tuple, list)):
                new_right = list(right)
                new_right.remove(sel)
                if new_right:
                    type_dom = [(left, op, new_right)]
                    if "service" in new_right:
                        # when service is in new_right we don't need to check service_tracking since they are _also_ services
                        return type_dom
            path = "".join(left.rpartition(".")[0:2])
            tracking_domain = [
                "&",
                (f"{path}type", "=", "service"),
                (f"{path}service_tracking", "=", sel),
            ]
            if op not in ["=", "in"]:
                tracking_domain.insert(0, "!")
            return expression.OR([type_dom, tracking_domain])
        return [leaf]

    if util.module_installed(cr, "event_sale"):
        adapter_event = partial(adapter, sel="event")
        util.adapt_domains(cr, "product.template", "detailed_type", "detailed_type", adapter=adapter_event)

    if util.module_installed(cr, "event_booth_sale"):
        adapter_event_booth = partial(adapter, sel="event_booth")
        util.adapt_domains(cr, "product.template", "detailed_type", "detailed_type", adapter=adapter_event_booth)

    if util.module_installed(cr, "website_sale_slides"):
        adapter_course = partial(adapter, sel="course")
        util.adapt_domains(cr, "product.template", "detailed_type", "detailed_type", adapter=adapter_course)

    util.update_field_usage(cr, "product.template", "type", "detailed_type")
    util.remove_field(cr, "product.template", "type")
    util.rename_field(cr, "product.template", "detailed_type", "type")
