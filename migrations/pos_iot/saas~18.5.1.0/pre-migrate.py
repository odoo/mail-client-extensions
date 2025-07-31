from odoo.upgrade import util


def migrate(cr, version):
    # Install the new separate Adam scale module for those who are using them
    cr.execute("SELECT 1 FROM iot_device WHERE type = 'scale' AND manufacturer = 'Adam' LIMIT 1")
    if cr.rowcount:
        util.force_install_module(cr, "pos_iot_adam_scale")
