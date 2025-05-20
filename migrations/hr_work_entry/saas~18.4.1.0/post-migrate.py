from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_work_entry.ir_cron_generate_missing_work_entries")
