# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "l10n_latam_document_type", "l10n_cl_active", "boolean")
