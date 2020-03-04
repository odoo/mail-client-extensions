# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Stages that were present from Odoo 6.0 to Odoo 8.0.
    # They are supposed to be in noupdate, but the noupdate flag was added as a bug fix after the release
    # odoo/odoo@40f974bfc181fd814e656a75866bbeb36f861f76
    # Therefore, as they are noupdate False, at the end of the upgrade, they get deleted,
    # and if they are still referenced, it raises.
    util.delete_unused(
        cr,
        "project.project_tt_analysis",
        "project.project_tt_cancel",
        "project.project_tt_deployment",
        "project.project_tt_design",
        "project.project_tt_development",
        "project.project_tt_merge",
        "project.project_tt_specification",
        "project.project_tt_testing",
    )
