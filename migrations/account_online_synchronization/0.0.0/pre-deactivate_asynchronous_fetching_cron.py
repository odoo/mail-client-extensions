from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("17.0", "saas~18.2"):
        util.update_record_from_xml(
            cr,
            "account_online_synchronization.online_sync_cron_waiting_synchronization",
        )
