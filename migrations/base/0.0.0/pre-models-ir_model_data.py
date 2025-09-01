from odoo import api, models, release
from odoo.tools.parse_version import parse_version

from odoo.addons.base.maintenance.migrations import util

if util.version_gte("10.0"):
    from odoo.modules.module import get_resource_from_path
else:
    get_resource_from_path = None
if parse_version(release.version) < parse_version("saas~11.4"):
    context_key_install = "install_mode_data"
else:
    context_key_install = "install_filename"


def migrate(cr, version):
    pass


if parse_version("10.0") <= parse_version(release.version) < parse_version("saas~11.5"):

    class IrModelData(models.Model):
        _inherit = "ir.model.data"
        _module = "base"

        # Force the update of `arch_fs` and the view validation even if the view has been set to noupdate.
        # Until saas-11.5, `_update` of ir.model.data is the method loading the data,
        # and choosing if the record must be overriden according the `noupdate` boolean
        @api.model
        def _update(self, model, module, values, xml_id=False, store=True, noupdate=False, mode="init", res_id=False):
            force_check_view = None
            if context_key_install in self.env.context and xml_id and model == "ir.ui.view":
                if "." in xml_id:
                    module, xml_id = xml_id.split(".")
                external_identifier = self.env["ir.model.data"].search([("module", "=", module), ("name", "=", xml_id)])
                if external_identifier.noupdate:
                    if parse_version(release.version) < parse_version("saas~11.4"):
                        filename = self.env.context[context_key_install]["xml_file"]
                    else:
                        filename = self.env.context[context_key_install]
                    xml_file = get_resource_from_path(filename)
                    if xml_file:
                        view = self.env["ir.ui.view"].browse(external_identifier.res_id)
                        orig_log_access = view._log_access
                        view._log_access = False
                        view.arch_fs = "/".join(xml_file[0:2])
                        view._log_access = orig_log_access
                        force_check_view = view
            res = super(IrModelData, self)._update(
                model, module, values, xml_id=xml_id, store=store, noupdate=noupdate, mode=mode, res_id=res_id
            )
            if force_check_view:
                # Standard View set to noupdate in database are no validated. Force the validation.
                # See https://github.com/odoo/odoo/pull/40207
                # Otherwise, if there is a validation issue, the upgrade won't block
                # but the user won't be able to open the view.
                force_check_view._check_xml()
            return res
