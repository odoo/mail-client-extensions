# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Update the field old_operation_id and new_operation_id depending of the related bom of mrp.eco
    # For old_operation_id: eco_id -> eco.bom_id -> new_operation.bom_id,
    #  rebase_id -> eco.bom_id -> new_operation.bom_id, eco_rebase_id -> eco.bom_id -> new_operation.bom_id
    # For new_operation_id: eco_id -> eco.new_bom_id -> new_operation.bom_id,
    #  rebase_id -> eco.bom_id -> new_operation.bom_id, eco_rebase_id -> eco.current_bom_id -> new_operation.bom_id
    cr.execute(
        """
        WITH select_eco_bom_change_old_operation AS (
            SELECT mrp_eco_bom_change.id AS id,
                   mrp_eco_bom_change.old_operation_id AS old_ope_id,
                   mrp_bom.id AS bom_id
              FROM mrp_eco_bom_change
                   JOIN mrp_eco
                        ON mrp_eco_bom_change.eco_id = mrp_eco.id
                           OR mrp_eco_bom_change.rebase_id = mrp_eco.id
                           OR mrp_eco_bom_change.eco_rebase_id = mrp_eco.id
                   JOIN mrp_bom ON mrp_eco.bom_id = mrp_bom.id
        )
        UPDATE mrp_eco_bom_change
           SET old_operation_id = temp_new_mrp_operation.id
          FROM select_eco_bom_change_old_operation
               JOIN temp_new_mrp_operation
                    ON temp_new_mrp_operation.bom_id = select_eco_bom_change_old_operation.bom_id
                       AND temp_new_mrp_operation.old_id = select_eco_bom_change_old_operation.old_ope_id
         WHERE select_eco_bom_change_old_operation.id = mrp_eco_bom_change.id
        """
    )
    cr.execute(
        """
        WITH select_eco_bom_change_temp_new_mrp_operation AS (
            SELECT mrp_eco_bom_change.id AS id,
                   mrp_eco_bom_change.old_operation_id AS old_ope_id,
                   mrp_bom.id AS bom_id
              FROM mrp_eco_bom_change
                   JOIN mrp_eco ON mrp_eco_bom_change.eco_id = mrp_eco.id
                   JOIN mrp_bom ON mrp_eco.new_bom_id = mrp_bom.id
             UNION
            SELECT mrp_eco_bom_change.id AS id,
                   mrp_eco_bom_change.old_operation_id AS old_ope_id,
                   mrp_bom.id AS bom_id
              FROM mrp_eco_bom_change
                   JOIN mrp_eco ON mrp_eco_bom_change.rebase_id = mrp_eco.id
                   JOIN mrp_bom ON mrp_eco.bom_id = mrp_bom.id
             UNION
            SELECT mrp_eco_bom_change.id AS id,
                   mrp_eco_bom_change.old_operation_id AS old_ope_id,
                   mrp_bom.id AS bom_id
              FROM mrp_eco_bom_change
                   JOIN mrp_eco ON mrp_eco_bom_change.eco_rebase_id = mrp_eco.id
                   JOIN mrp_bom ON mrp_eco.current_bom_id = mrp_bom.id
        )
        UPDATE mrp_eco_bom_change
           SET old_operation_id = temp_new_mrp_operation.id
          FROM select_eco_bom_change_temp_new_mrp_operation
               JOIN temp_new_mrp_operation
                    ON temp_new_mrp_operation.bom_id = select_eco_bom_change_temp_new_mrp_operation.bom_id
                       AND temp_new_mrp_operation.old_id = select_eco_bom_change_temp_new_mrp_operation.old_ope_id
         WHERE select_eco_bom_change_temp_new_mrp_operation.id = mrp_eco_bom_change.id
        """
    )

    util.remove_field(cr, "mrp.eco", "new_routing_revision")
    util.remove_field(cr, "mrp.eco", "new_routing_id")
    util.remove_field(cr, "mrp.eco", "routing_id")

    util.remove_record(cr, "mrp_plm.mrp_eco_action_routing")
    util.remove_menus(cr, [util.ref(cr, "mrp_plm.menu_mrp_plm_routings")])
