from odoo.upgrade import util


def migrate(cr, version):
    util.remove_inherit_from_model(cr, "maintenance.equipment.category", "mail.thread")
    util.remove_inherit_from_model(cr, "maintenance.equipment.category", "mail.alias.mixin")

    util.add_to_migration_reports(
        "The mail alias on the equipment category has been removed. You can recreate them on the maintenance team instead.",
        "Maintenance",
    )
