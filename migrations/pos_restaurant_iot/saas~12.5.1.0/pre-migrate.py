# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "restaurant_printer", "device_id", "int4")

    # 1. `device_id` is added, and can be determined from the `iotbox_id`, which has been removed.
    # A same iot box can have multiple printers. Here, the selection criteria is the connection and the id
    # but the customer might want to select another device after the upgrade.
    cr.execute(
        """
        UPDATE restaurant_printer
           SET device_id = (
                     SELECT id
                       FROM iot_device
                      WHERE iot_id = iotbox_id
                        AND type = 'printer'
                   ORDER BY connection, id -- order by connect because `direct` (USB) is better than `network`.
                      LIMIT 1
               )
         WHERE iotbox_id IS NOT NULL
        """
    )

    # 2. Remove the field and column `iotbox_id`
    util.remove_field(cr, "restaurant.printer", "iotbox_id")
