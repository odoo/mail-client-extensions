# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Remove children of theme_common._assets_primary_variables since their parent will be removed
    util.remove_record(cr, "theme_common.option_colors_09_variables")
    util.remove_record(cr, "theme_common.option_colors_08_variables")
    util.remove_record(cr, "theme_common.option_colors_07_variables")
    util.remove_record(cr, "theme_common.option_colors_06_variables")
    util.remove_record(cr, "theme_common.option_colors_05_variables")
    util.remove_record(cr, "theme_common.option_colors_04_variables")
    util.remove_record(cr, "theme_common.option_colors_03_variables")
    util.remove_record(cr, "theme_common.option_colors_02_variables")
    # Remove view loading deprecated snippet files
    for (
        theme
    ) in "bewise graphene enark avantgarde nano paptic treehouse zap bistro clean\
                  cobalt real_estate odoo_experts yes orchid artists vehicle kiddo\
                  anelusia beauty bookstore monglia loftspace notes kea common".split():
        util.remove_record(cr, "theme_%s._assets_primary_variables" % theme)
        util.remove_record(cr, "theme_%s._assets_secondary_variables" % theme)
