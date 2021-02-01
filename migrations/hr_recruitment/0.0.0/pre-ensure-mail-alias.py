from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ensure_xmlid_match_record(cr, "hr_recruitment.mail_alias_jobs", "mail.alias", {"alias_name": "jobs"})
