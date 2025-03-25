from odoo.fields import Datetime

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    xmlid = "mail.ir_cron_module_update_notification"
    util.update_record_from_xml(cr, xmlid)
    cron = util.env(cr)["ir.cron"].browse(util.ref(cr, xmlid))
    cron.write({"active": True, "nextcall": Datetime.now()})
