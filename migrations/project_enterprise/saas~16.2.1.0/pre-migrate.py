from odoo.upgrade import util


def migrate(cr, version):
    if not util.version_gte("saas~16.5"):
        # in new versions, the `allocated_hours` fields are actually the `planned_hours` fields that has been renamed. We SHOULD not remove them.
        util.remove_field(cr, "project.task", "allocated_hours")
        util.remove_field(cr, "report.project.task.user", "allocated_hours")
    util.remove_field(cr, "project.task", "allocation_type")
    util.remove_field(cr, "project.task", "duration")
