from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "pos_config", "iface_printer_id", "int4")
    util.create_column(cr, "pos_config", "iface_display_id", "int4")
    util.create_column(cr, "pos_config", "iface_scale_id", "int4")
    util.create_column(cr, "pos_payment_method", "iot_device_id", "int4")

    util.remove_field(cr, "account.journal", "use_payment_terminal")
    util.remove_field(cr, "pos.config", "iface_payment_terminal")

    # `iface_printer_id`, `iface_display_id` and `iface_scale_id` are added, and can be determined from the `iotbox_id`,
    # which has been removed.
    # A same iot box can have multiple devices, multiple printers, multiple displays, multiple scales.
    # in 12.0, the device was chosen by the Javascript, it took the first device available,
    # in 13.0, you can choose by pos config the device to use on the iot box.

    # 1. Determine the printer, display and scale to use by pos config. It's an heuristic,
    #    the user might want to change this after upgrade if it does not suit his requirements.
    cr.execute(
        """
        UPDATE pos_config
           SET iface_printer_id = (
                     SELECT id
                       FROM iot_device
                      WHERE iot_id = iotbox_id
                        AND type = 'printer'
                   ORDER BY connection, id -- order by connect because `direct` (USB) is better than `network`.
                      LIMIT 1
               ),
               iface_display_id = (
                      SELECT id
                        FROM iot_device
                       WHERE iot_id = iotbox_id
                         AND type = 'display'
                    ORDER BY connection, id
                       LIMIT 1
               ),
               iface_scale_id = (
                      SELECT id
                        FROM iot_device
                       WHERE iot_id = iotbox_id
                         AND type = 'scale'
                    ORDER BY connection, id
                       LIMIT 1
               )
         WHERE iotbox_id IS NOT NULL
        """
    )

    # 2. Remove the field and column `iotbox_id`
    util.remove_field(cr, "pos.config", "iotbox_id")

    # 3. Remove fields overridden to be non-stored
    util.remove_column(cr, "pos_config", "iface_electronic_scale")
    util.remove_column(cr, "pos_config", "iface_customer_facing_display")
    util.remove_column(cr, "pos_config", "iface_print_via_proxy")
    util.remove_column(cr, "pos_config", "iface_scan_via_proxy")
