import logging

from openerp import models
from openerp.modules.module import get_modules
from openerp.addons.base.maintenance.migrations import util
if util.version_gte('10.0'):
    from openerp.modules.module import get_resource_path, get_resource_from_path
    if util.version_gte('saas~11.4'):
        from openerp.addons.base.models.ir_ui_view import get_view_arch_from_file
    else:
        from openerp.addons.base.ir.ir_ui_view import get_view_arch_from_file
else:
    get_resource_path = get_resource_from_path = get_view_arch_from_file = None


_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base." + __name__)


def migrate(cr, version):
    pass


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'
    _module = 'base'

    if util.version_gte('10.0'):
        def _migrate_get_roots(self):
            roots = self.env['ir.ui.view']
            for view in self:
                while view.inherit_id:
                    view = view.inherit_id
                roots |= view
            return roots

        def _check_xml(self):
            try:
                return super(IrUiView, self)._check_xml()
            except Exception:
                if self._migrate_fix_views():
                    return self._migrate_get_roots()._check_xml()
                else:
                    raise

        def _migrate_fix_views(self):
            # If a view has validation issue, either:
            # - Overwrite the arch if this is a standard view for which the user manually set it to noupdate,
            # - Disable the view if this is a custom view
            # The algorithm tries to correct one view at a time and then re-attempt the validation,
            # so if there are multiple custom views but only one causes an issue, it tries to disable only this one.
            standard_modules = get_modules()
            custom_modules = [r['name'] for r in self.env['ir.module.module'].search_read([
                ('name', 'not in', standard_modules)
            ], ['name'])]
            views_to_check = []
            views = self._migrate_get_roots()
            while views:
                for view in views:
                    if view.active:
                        views_to_check.insert(0, view)
                views = views.mapped('inherit_children_ids')
            for view in views_to_check:
                md = self.env['ir.model.data'].search([
                    ('model', '=', 'ir.ui.view'), ('res_id', '=', view.id)
                ], limit=1)
                arch_fs_fullpath = get_resource_path(*view.arch_fs.split('/')) if view.arch_fs else False
                if arch_fs_fullpath and md and md.noupdate and md.module:
                    # Standard view set to noupdate by the user, to override with original view
                    md.noupdate = False
                    view.arch_db = get_view_arch_from_file(arch_fs_fullpath, view.xml_id)
                    # Mark the view as it was loaded with its XML data file.
                    # Otherwise it will be deleted in _process_end
                    if util.version_gte('saas~11.5'):
                        self.pool.loaded_xmlids.add('%s.%s' % (md.module, md.name))
                    else:
                        self.pool.model_data_reference_ids[(md.module, md.name)] = (view._name, view.id)
                    _logger.warning("""
                        The standard view `%s.%s` was set to `noupdate` and caused validation issues.
                        Resetting its arch and noupdate flag for the migration ...
                    """, md.module, md.name)
                    return True
                elif not md or md.module not in standard_modules:
                    if md.module in custom_modules:
                        # custom view in a custom module, to remove
                        # it will be re-created when the user call -u on its custom module
                        view.unlink()
                    else:
                        # Custom view not in a custom module, to disable
                        view.active = False
                    _logger.warning("""
                        The custom view `%s` (ID: %s, Inherit: %s, Model: %s) caused validation issues.
                        Disabling it for the migration ...
                    """, view.name, view.id, view.inherit_id, view.model)
                    return True
                view = view.inherit_id
            else:
                # No view has been modified
                return False

        if util.version_gte('saas~11.5'):
            # Force the update of arch_fs and the view validation even if the view has been set to noupdate.
            # From saas-11.5, `_update` of ir.model.data is deprecated and replaced by _load_records on each models
            def _load_records(self, data_list, update=False):
                xml_ids = [data['xml_id'] for data in data_list if data.get('xml_id')]
                force_check_views = self.env['ir.ui.view']
                for row in self.env['ir.model.data']._lookup_xmlids(xml_ids, self):
                    d_id, d_module, d_name, d_model, d_res_id, d_noupdate, r_id = row
                    if d_noupdate:
                        filename = self.env.context['install_filename']
                        xml_file = get_resource_from_path(filename)
                        if xml_file:
                            view = self.browse(d_res_id)
                            view.arch_fs = '/'.join(xml_file[0:2])
                            force_check_views |= view
                res = super(IrUiView, self)._load_records(data_list, update=update)
                # Standard View set to noupdate in database are no validated. Force the validation.
                # See https://github.com/odoo/odoo/pull/40207
                # Otherwise, if there is a validation issue, the upgrade won't block
                # but the user won't be able to open the view.
                force_check_views._check_xml()
                return res
