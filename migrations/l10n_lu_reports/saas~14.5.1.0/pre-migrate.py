# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===========================================================
    # Task 2526717 : Agent / Fiduciary for XML exports
    # ===========================================================
    util.create_column(cr, "res_partner", "l10n_lu_agent_matr_number", "varchar")
    util.create_column(cr, "res_partner", "l10n_lu_agent_ecdf_prefix", "varchar")
    util.create_column(cr, "res_partner", "l10n_lu_agent_rcs_number", "varchar")
