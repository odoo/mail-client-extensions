import logging
import os
import re

from odoo import api, models
from odoo.modules.module import get_modules
from odoo.tools.misc import str2bool

from odoo.addons.base.maintenance.migrations import util

if util.version_gte("10.0"):
    from odoo.modules.module import get_resource_from_path, get_resource_path
    from odoo.tools.view_validation import _validators

    if util.version_gte("saas~11.1"):
        from odoo.addons.base.models.ir_ui_view import get_view_arch_from_file
    else:
        from odoo.addons.base.ir.ir_ui_view import get_view_arch_from_file
else:
    get_resource_path = get_resource_from_path = get_view_arch_from_file = None
    _validators = {}

try:
    from odoo.tools.pycompat import to_text
except ImportError:
    to_text = lambda t: t


_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base." + __name__)


def migrate(cr, version):
    pass


def get_standard_modules(self):
    if not util.ENVIRON.get("standard_modules"):
        standard_modules = get_modules()
        modules = self.env["ir.module.module"].search_read(
            [("name", "in", standard_modules), ("state", "in", ["installed", "to upgrade", "to install"])], ["name"]
        )
        util.ENVIRON["standard_modules"] = [module["name"] for module in modules]
    return util.ENVIRON["standard_modules"]


class IrUiView(models.Model):
    _inherit = "ir.ui.view"
    _module = "base"

    if util.version_gte("10.0"):

        def _check_xml(self):
            # Do not validate views during the upgrade. All views will be validated at once after upgrade.
            if not self.env.context.get("_upgrade_validate_views"):
                return True
            res = True
            for record in self.with_context(_migrate_enable_studio_check=True):
                try:
                    res = res and super(IrUiView, record)._check_xml()
                except Exception:
                    if record._migrate_fix_views():
                        # The current view might have been disabled, so find the root and validate it.
                        view = record
                        while view.mode != "primary":
                            view = view.inherit_id
                        res = res and view._check_xml()
                    else:
                        raise
            return res

        def copy_translations(old, new, *args, **kwargs):
            if old.env.context.get("_migrate_fix_views"):
                return
            return super(IrUiView, old).copy_translations(new, *args, **kwargs)

        def _migrate_fix_views(self):
            # If a view has validation issue, either:
            # - Overwrite the arch if this is a standard view for which the user manually set it to noupdate,
            # - Disable the view if this is a custom view
            # The algorithm tries to correct one view at a time and then re-attempt the validation,
            # so if there are multiple custom views but only one causes an issue, it tries to disable only this one.

            def resolve_external_ids(arch_fs, module):
                def replacer(m):
                    xmlid = m.group("xmlid")
                    if "." not in xmlid:
                        xmlid = "%s.%s" % (module, xmlid)
                    return m.group("prefix") + str(self.env["ir.model.data"].xmlid_to_res_id(xmlid))

                return re.sub(r"(?P<prefix>[^%])%\((?P<xmlid>.*?)\)[ds]", replacer, arch_fs)

            standard_modules = get_standard_modules(self)
            views_to_check = []
            views = self.env["ir.ui.view"]
            for view in self:
                while view.inherit_id:
                    view = view.inherit_id
                views |= view
            while views:
                for view in views:
                    if view.active:
                        views_to_check.insert(0, view)
                views = views.mapped("inherit_children_ids")
            for view in views_to_check:
                md = self.env["ir.model.data"].search([("model", "=", "ir.ui.view"), ("res_id", "=", view.id)], limit=1)
                arch_fs_fullpath = get_resource_path(*view.arch_fs.split("/")) if view.arch_fs else False
                view_data = {
                    "id": view.id,
                    "name": view.name,
                    "model": view.model,
                    "inherit_id": view.inherit_id,
                    "module": md.module,
                    "xml_id": "%s.%s" % (md.module, md.name),
                    "arch_fs": view.arch_fs,
                }
                if arch_fs_fullpath and md and md.noupdate and md.module:
                    # Standard view set to noupdate by the user, to override with original view
                    md.noupdate = False
                    view_copy = view.with_context(_migrate_fix_views=True).copy(
                        {"active": False, "name": "%s (Copy created during upgrade)" % view.name}
                    )
                    view_data["copy_id"] = view_copy.id
                    arch_db = get_view_arch_from_file(arch_fs_fullpath, view.xml_id)
                    view.arch_db = to_text(resolve_external_ids(arch_db, md.module).replace("%%", "%"))
                    # Mark the view as it was loaded with its XML data file.
                    # Otherwise it will be deleted in _process_end
                    if util.version_gte("saas~11.5"):
                        self.pool.loaded_xmlids.add("%s.%s" % (md.module, md.name))
                    else:
                        self.pool.model_data_reference_ids[(md.module, md.name)] = (view._name, view.id)
                    util.add_to_migration_reports(view_data, "Overridden views")
                    _logger.warning(
                        """
                        The standard view `%s.%s` was set to `noupdate` and caused validation issues.
                        Resetting its arch and noupdate flag for the migration ...
                    """,
                        md.module,
                        md.name,
                    )
                    return True
                elif not md or md.module not in standard_modules:
                    message = "The custom view `%s` (ID: %s, Inherit: %s, Model: %s) caused validation issues." % (
                        view.name,
                        view.id,
                        view.inherit_id.id,
                        view.model,
                    )
                    util.add_to_migration_reports(view_data, "Disabled views")
                    _logger.warning(
                        """
                    %s
                    Disabling it for the migration ...
                    """,
                        message,
                    )
                    view.active = False
                    act_window = self.env["ir.actions.act_window"]
                    act_window.search([("view_id", "=", view.id)]).write({"view_id": False})
                    act_window.search([("search_view_id", "=", view.id)]).write({"search_view_id": False})
                    self.env["ir.actions.act_window.view"].search([("view_id", "=", view.id)]).unlink()
                    return True
                view = view.inherit_id
            else:
                # No view has been modified
                return False

        @api.model
        def _register_hook(self):
            """
            Validate all views, whether custom or not,
            with the fields coming from custom modules loaded as manual fields.
            """
            super(IrUiView, self)._register_hook()
            origin_validators = dict(_validators)
            dummy_validators = dict.fromkeys(_validators, [lambda *args, **kwargs: True])
            standard_modules = tuple(get_standard_modules(self))
            queries = [
                """
                       SELECT max(v.id)
                         FROM ir_ui_view v
                         JOIN ir_model_data md ON (md.model = 'ir.ui.view' AND md.res_id = v.id)
                        WHERE md.module IN %(modules)s
                          AND v.active
                     GROUP BY CASE WHEN v.mode = 'extension' THEN coalesce(v.inherit_id, v.id) ELSE v.id END
                """,
                """
                       SELECT max(v.id)
                        FROM ir_ui_view v
                        LEFT JOIN ir_model_data md ON (md.model = 'ir.ui.view' AND md.res_id = v.id)
                       WHERE md.module NOT IN %(modules)s OR md.module IS NULL
                         AND v.active
                    GROUP BY CASE WHEN v.mode = 'extension' THEN coalesce(v.inherit_id, v.id) ELSE v.id END
                """,
            ]
            with util.custom_module_field_as_manual(self.env):
                for is_custom_modules, query in enumerate(queries):
                    self._cr.execute(query, {"modules": standard_modules})
                    views = self.browse(it[0] for it in self._cr.fetchall())
                    if is_custom_modules:
                        _validators.update(dummy_validators)
                    for view in views.with_context(
                        _upgrade_validate_views=True,
                        load_all_views=is_custom_modules,
                        _upgrade_custom_modules=is_custom_modules,
                    ):
                        if view.model not in self.env.registry:
                            continue
                        try:
                            view._check_xml()
                        except Exception:
                            _logger.exception("invalid custom view %s for model %s", view.xml_id or view.id, view.model)
            _validators.update(origin_validators)

        if util.version_gte("saas~11.5"):
            # Force the update of arch_fs and the view validation even if the view has been set to noupdate.
            # From saas-11.5, `_update` of ir.model.data is deprecated and replaced by _load_records on each models
            def _load_records(self, data_list, update=False):
                xml_ids = [data["xml_id"] for data in data_list if data.get("xml_id")]
                force_check_views = self.env["ir.ui.view"]
                for row in self.env["ir.model.data"]._lookup_xmlids(xml_ids, self):
                    d_id, d_module, d_name, d_model, d_res_id, d_noupdate, r_id = row
                    if d_noupdate:
                        filename = self.env.context["install_filename"]
                        xml_file = get_resource_from_path(filename)
                        if xml_file:
                            view = self.browse(d_res_id)
                            view.arch_fs = "/".join(xml_file[0:2])
                            force_check_views |= view
                res = super(IrUiView, self)._load_records(data_list, update=update)
                # Standard View set to noupdate in database are no validated. Force the validation.
                # See https://github.com/odoo/odoo/pull/40207
                # Otherwise, if there is a validation issue, the upgrade won't block
                # but the user won't be able to open the view.
                force_check_views._check_xml()
                return res

    if util.version_gte("saas~13.1"):

        def unlink(self):
            for view in self:
                if view.xml_id:
                    if "view:%s" % (view.xml_id) in os.environ.get("suppress_upgrade_warnings", "").split(","):
                        _logger.log(25, "View unlink %s explicitly ignored", (view.xml_id))
                    else:
                        _logger.critical("It looks like you forgot to call `util.remove_view(cr, %r)`", view.xml_id)
                        if str2bool(os.getenv("MATT", "0")):
                            # Hard fail only in CI.
                            raise util.MigrationError(
                                "It looks like you forgot to call `util.remove_view(cr, %r)`" % view.xml_id
                            )

            return super().unlink()

        def _validate_tag_button(self, *args, **kwargs):
            if self.env.context.get("_upgrade_custom_modules"):
                return
            return super()._validate_tag_button(*args, **kwargs)

        def _validate_tag_label(self, *args, **kwargs):
            if self.env.context.get("_upgrade_custom_modules"):
                return
            return super()._validate_tag_label(*args, **kwargs)
