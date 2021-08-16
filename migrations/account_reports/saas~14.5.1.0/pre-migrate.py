# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.aged.partner", "journal_code")
    # ===========================================================
    # Task 2526717 : Agent / Fiduciary for XML exports
    # ===========================================================
    util.create_column(cr, "res_company", "account_representative_id", "int4")
    # ===========================================================
    # Task 2613022 : UX/UI Control Domains on Financial Reports
    # ===========================================================
    util.remove_view(cr, "account_reports.line_template_control_domain")
