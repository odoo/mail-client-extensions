from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_hr_recruitment.default_description", util.update_record_from_xml)
