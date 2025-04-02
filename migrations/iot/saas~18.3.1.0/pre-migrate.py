from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "iot.box", "is_websocket_active")

    util.create_column(cr, "iot_device", "connected_status", "varchar")
    cr.execute(
        """
        UPDATE iot_device
           SET connected_status = CASE
                                      WHEN connected THEN 'connected'
                                      ELSE 'disconnected'
                                   END
        """
    )
    util.remove_field(cr, "iot.device", "connected")
