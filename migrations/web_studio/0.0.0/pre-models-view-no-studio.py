# -*- coding: utf-8 -*-
from odoo import models

from odoo.addons.web_studio.models import ir_ui_view  # noqa


def migrate(cr, version):
    pass


class IrUiView(models.Model):
    _inherit = "ir.ui.view"
    _module = "web_studio"

    def _is_studio_view(self):
        # This shit is only used in one place:
        # in the `apply_inheritance_specs` override in studio
        # to determine if the view should raise if its invalid, according if its a studio view or not
        # we want studio views to be validated during upgrades, so they are disabled if they do not work
        # https://github.com/odoo/enterprise/commit/b56101200ac35dae3eadbc0bdf4ba17461f33907#diff-b87200ad8cd0d8ee381611dfbca8d518R109
        # The context key used below is added in the override of `_check_xml` in base/0.0.0/pre-models-ir_ui_view.py
        if self.env.context.get("_migrate_enable_studio_check"):
            return False
        return super(IrUiView, self)._is_studio_view()
