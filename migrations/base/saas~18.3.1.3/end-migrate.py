from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "base.default_user", keep_xmlids=False)

    mapping = {
        "base.module_category_inventory": "base.module_category_supply_chain",
        "base.module_category_inventory_inventory": "base.module_category_supply_chain_inventory",
        "base.module_category_inventory_delivery": "base.module_category_shipping_connectors",
        "base.module_category_inventory_purchase": "base.module_category_supply_chain_purchase",
        "base.module_category_manufacturing": "base.module_category_supply_chain",
        "base.module_category_manufacturing_manufacturing": "base.module_category_supply_chain_manufacturing",
        "base.module_category_manufacturing_purchase": "base.module_category_supply_chain_purchase",
        "base.module_category_manufacturing_internet_of_things_(iot)": "base.module_category_supply_chain_internet_of_things_(iot)",
        "base.module_category_manufacturing_product_lifecycle_management_(plm)": "base.module_category_supply_chain_product_lifecycle_management_(plm)",
        "base.module_category_manufacturing_maintenance": "base.module_category_supply_chain_maintenance",
        "base.module_category_manufacturing_repair": "base.module_category_supply_chain_repair",
        "base.module_category_repair_purchase": "base.module_category_supply_chain_purchase",
        "base.module_category_repair_quality": "base.module_category_supply_chain_quality",
        "base.module_category_marketing_whatsapp": "base.module_category_productivity_whatsapp",
        "base.module_category_localization_point_of_sale": "base.module_category_sales_point_of_sale",
    }

    id_map = {util.ref(cr, k): util.ref(cr, v) for k, v in mapping.items()}
    util.replace_record_references_batch(cr, id_map, "ir.module.category", replace_xmlid=False)
    util.delete_unused(cr, *list(mapping))
