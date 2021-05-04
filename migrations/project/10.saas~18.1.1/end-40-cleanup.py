# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for f in "issue_count issue_ids label_issues use_issues issue_needaction_count".split():
        util.remove_field(cr, "project.project", f)
    util.remove_field(cr, "account.analytic.account", "use_issues")
    util.remove_field(cr, "res.partner", "issue_count")
    util.remove_field(cr, "account.analytic.line", "issue_id")  # from `project_issue_sheet`

    cr.execute(
        """
        DELETE FROM ir_server_object_lines l
              USING ir_model_fields f
              WHERE l.col1=f.id
                AND f.model='project.issue';
    """
    )
    util.remove_model(cr, "project.issue")
    util.remove_model(cr, "project.issue.report")  # from <= saas~16
