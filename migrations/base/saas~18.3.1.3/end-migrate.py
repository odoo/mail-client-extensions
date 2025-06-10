import logging

import odoo

from odoo.upgrade import util

_logger = logging.getLogger("odoo.upgrade.base/saas~18.3")


def migrate(cr, version):
    rm = True
    if util.table_exists(cr, "hr_employee"):
        # The `default_user` may be linked to an employee record. (see https://upgrade.odoo.com/odoo/action-178/2028)
        query = """
            DELETE
              FROM ir_model_data d
             WHERE d.module = 'base'
               AND d.name = 'default_user'
               AND EXISTS(SELECT 1 FROM hr_employee e WHERE e.user_id = d.res_id)
        """
        cr.execute(query)
        rm = not bool(cr.rowcount)

    if rm:
        util.remove_record(cr, "base.default_user")

    community_mapping = {
        "base.module_category_inventory": "base.module_category_supply_chain",
        "base.module_category_inventory_inventory": "base.module_category_supply_chain_inventory",
        "base.module_category_inventory_delivery": "base.module_category_shipping_connectors",
        "base.module_category_inventory_purchase": "base.module_category_supply_chain_purchase",
        "base.module_category_manufacturing": "base.module_category_supply_chain",
        "base.module_category_manufacturing_manufacturing": "base.module_category_supply_chain_manufacturing",
        "base.module_category_manufacturing_purchase": "base.module_category_supply_chain_purchase",
        "base.module_category_manufacturing_maintenance": "base.module_category_supply_chain_maintenance",
        "base.module_category_manufacturing_repair": "base.module_category_supply_chain_repair",
        "base.module_category_repair_purchase": "base.module_category_supply_chain_purchase",
        "base.module_category_localization_point_of_sale": "base.module_category_sales_point_of_sale",
    }
    enterprise_mapping = {
        "base.module_category_manufacturing_internet_of_things_(iot)": "base.module_category_supply_chain_internet_of_things_(iot)",
        "base.module_category_manufacturing_product_lifecycle_management_(plm)": "base.module_category_supply_chain_product_lifecycle_management_(plm)",
        "base.module_category_repair_quality": "base.module_category_supply_chain_quality",
        "base.module_category_marketing_whatsapp": "base.module_category_productivity_whatsapp",
    }
    mapping = {**community_mapping, **enterprise_mapping} if util.has_enterprise() else community_mapping

    id_map = {util.ref(cr, k): util.ref(cr, v) for k, v in mapping.items()}
    id_map.pop(None, None)
    util.replace_record_references_batch(cr, id_map, "ir.module.category", replace_xmlid=False)
    util.delete_unused(cr, *list(mapping))

    # force updating new privilege field for existing groups
    cr.execute(
        """
        SELECT imd.module || '.' || imd.name
          FROM ir_model_data AS imd
          JOIN res_groups AS g
            ON imd.model = 'res.groups'
           AND imd.res_id = g.id
         WHERE imd.module IN %s
        """,
        [tuple(odoo.modules.get_modules())],
    )
    for (xmlid,) in cr.fetchall():
        try:
            util.update_record_from_xml(cr, xmlid, fields=["privilege_id"])
        except ValueError:
            _logger.info("unable to update group privilege info of '%s', record not found in xml", xmlid)
