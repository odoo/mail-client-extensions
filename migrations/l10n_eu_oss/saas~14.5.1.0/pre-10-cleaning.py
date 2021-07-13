# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.config.settings", "l10n_eu_services_eu_country", "l10n_eu_oss_eu_country")

    util.remove_model(cr, "l10n_eu_service.service_tax_rate")
    util.remove_model(cr, "l10n_eu_service.wizard")
