import itertools
import logging
import os
import re

try:
    from html import unescape
except ImportError:
    import HTMLParser

    unescape = HTMLParser.HTMLParser().unescape

try:
    zip = itertools.izip
except AttributeError:
    zip_longest = itertools.zip_longest
else:
    zip_longest = itertools.izip_longest

try:
    filterfalse = itertools.filterfalse
except AttributeError:
    filterfalse = itertools.ifilterfalse

from lxml import etree

from odoo import api, models
from odoo.modules.module import get_modules
from odoo.tools import mute_logger
from odoo.tools.misc import str2bool

from odoo.addons.base.maintenance.migrations import util

if util.version_gte("12.0"):
    from odoo.addons.base.maintenance.migrations.testing import DATA_TABLE
else:
    DATA_TABLE = None

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

    def to_text(t):
        return t


_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base." + __name__)
ODOO_MIG_TRY_FIX_VIEWS = str2bool(os.environ.get("ODOO_MIG_TRY_FIX_VIEWS", "0"))
STANDARD_IDS = set()


def migrate(cr, version):
    global ODOO_MIG_TRY_FIX_VIEWS

    if DATA_TABLE and util.table_exists(cr, DATA_TABLE):
        cr.execute("SELECT 1 FROM {} WHERE key='base.tests.test_fix_views.TestFixViews' LIMIT 1".format(DATA_TABLE))
        ODOO_MIG_TRY_FIX_VIEWS |= bool(cr.rowcount)  # force fixing views whenever TestFixViews.test_prepare was run

    cast = "->>'en_US' as arch_db" if util.column_type(cr, "ir_ui_view", "arch_db") == "jsonb" else ""
    cr.execute("SELECT id,model,arch_db{} INTO UNLOGGED ir_ui_view_data_backup FROM ir_ui_view".format(cast))
    cr.execute("ALTER TABLE ir_ui_view_data_backup ADD PRIMARY KEY(id)")

    # The ORM always use views set via search_view_id column or ir_act_window_view table.
    # Thus we activate them here in order to check them later on.
    # In case one of the views fail and cannot be fixed:
    # * for standard views, the view will remain active but will be restored from FS
    # * custom views will be disabled but also the link action->view will be removed
    # both cases will potentially fix issues with the views that otherwise may just fail.
    cr.execute(
        """
        UPDATE ir_ui_view v
           SET active = true
          FROM ir_act_window a
          JOIN ir_act_window_view av
            ON av.act_window_id = a.id
         WHERE v.active IS DISTINCT FROM true
           AND v.id IN (a.search_view_id, a.view_id, av.view_id)
        """
    )


#########################
# view backup utilities #
def view_backup(cr, view):
    cr.execute("SELECT * FROM ir_ui_view_data_backup WHERE id=%s", [view.id])
    return cr.dictfetchall()[0]


def get_parent_arch_bks(cr, view):
    parent_view = view.inherit_id
    while parent_view:
        # iterate only over primary parents?
        if parent_view.model in valid_models(view):
            yield etree.fromstring(view_backup(cr, parent_view)["arch_db"])
        parent_view = parent_view.inherit_id


##########################
# pretty print utilities #
def pp_xml_str(xml):
    return etree.tostring(etree.fromstring(xml), pretty_print=True).decode()


def pp_xml_elem(elem):
    return etree.tostring(elem, pretty_print=True).decode().splitlines()[0] + "..."


#################
# xml utilities #
def find_xpath_elem(arch, expr):
    for elem in arch.xpath("//xpath[@expr]"):
        elem_expr = elem.attrib["expr"]
        if expr in (elem_expr, unescape(elem_expr)):
            return elem


def get_closest_elements(elem):
    """
    Generate tuples of the form (element, anchoring_position) ordered by closedness to {elem}.
    Iterates over all the siblings of {elem} plus its parent, alternating one sibling before,
    one after. The last visited element is the parent.
    """
    iter_prev = zip(elem.itersiblings(preceding=True), itertools.repeat("after"))
    iter_next = zip(elem.itersiblings(), itertools.repeat("before"))
    for p, n in zip_longest(iter_prev, iter_next, fillvalue=(None, None)):
        if p[0] is not None:
            yield p
        if n[0] is not None:
            yield n
    yield (elem.getparent(), "inside")


def validate_expr(tree, elem, expr):
    elems = tree.xpath(expr)
    return len(elems) > 0 and elem == elems[0]


###################
# model utilities #
def valid_models(view):
    # get all models valid as model for parent views
    view_model = view.env[view.model]
    return (
        {view.model}
        | ({view_model._inherit} if isinstance(view_model._inherit, str) else set(view_model._inherit))
        | set(view_model._inherits)
    )


def field_change(view, name):
    # checks if the field was renamed or removed
    return any(name in util.ENVIRON["__renamed_fields"][model] for model in valid_models(view))


def field_new_name(view, name):
    info = getattr(field_new_name, "info", None)
    if info is None:
        # invert the relation, we want to know how an old field is named now
        info = {
            model: {old: new for new, old in fields.items() if old}
            for model, fields in util.ENVIRON["__renamed_fields"].items()
        }
        field_new_name.info = info
    # return field new name, if any
    for model in valid_models(view):
        if name in info.get(model, {}):
            return info[model][name]


def get_standard_modules(self):
    if not util.ENVIRON.get("standard_modules"):
        standard_modules = list(get_modules())
        modules = self.env["ir.module.module"].search_read(
            [("name", "in", standard_modules), ("state", "in", ["installed", "to upgrade", "to install"])], ["name"]
        )
        util.ENVIRON["standard_modules"] = [module["name"] for module in modules]
    return util.ENVIRON["standard_modules"] + ["test_upg"]  # for testing purposes


def is_standard_view(view):
    return view.id in STANDARD_IDS


def save_arch(view, arch):
    old_arch = view.arch
    view.arch = etree.tostring(arch, encoding="unicode")
    return old_arch


def heuristic_fixes(cr, view, check, e, tried_anchors=None):
    """
    Try to fix a failing view on xpath element not found following some heuristics (see the code for details).
    On each heuristic we check if the original exception {e} is not present anymore, if so then we recursively check
    the new exception if any.

    {tried_anchor} holds the pairs of old/new expr tried already, to avoid infinite recursion due to re-trying what
    was done already.

    Returns whether we could fix the view or not, always return True if {e} is None
    """
    if e is None:
        return True

    if tried_anchors is None:
        tried_anchors = set()

    def update_anchor(view, arch, xelem, orig_arch):
        """
        Tries to update the {arch} and {xelem} by checking if the original arch matches the xpath
        if so, then try updating the {xelem} to use as anchor another of the surrounding elements
        if there is no match or the modifications are not succesful then returns False

        In order to update the element we check the backuped archs of the parent views.
        """

        def get_expr(anchor, orig_arch):
            # TODO: extend this method to add more cases?
            #       for example we could chain hasclass to match multiple classes
            if anchor.tag == "field":
                yield '//{}[@name="{}"]'.format(anchor.tag, anchor.attrib.get("name", ""))
            if "class" in anchor.attrib:
                for klass in anchor.attrib["class"].split():
                    yield '//{}[hasclass("{}")]'.format(anchor.tag, klass)
            # try with a more precise xpath
            yield "/" + etree.ElementTree(orig_arch).getpath(anchor)
            # as last resort try matching only by tag...
            # not ideal though validate_expr will check it selects the right anchor
            yield "//" + anchor.tag

        for elem in orig_arch.xpath(xelem.attrib["expr"]):
            if elem.tag not in ("field", "filter"):
                # We only care about fields/filters, other changes would be too
                # complex/specific for automatic fixes
                continue

            for anchor, position in get_closest_elements(elem):
                for new_expr in get_expr(anchor, orig_arch):
                    if not validate_expr(orig_arch, anchor, new_expr):
                        continue
                    pair = (xelem.attrib["expr"], new_expr)
                    if pair in tried_anchors:
                        continue
                    tried_anchors.add(pair)
                    xelem.set("expr", new_expr)
                    xelem.set("position", position)
                    save_arch(view, arch)
                    new_e = check()
                    if new_e is None:
                        return True
                    # we need to check that the new exception is not due to what we just did
                    # otherwise we may get infinite recursion
                    m = re.search("Element '<xpath expr=.(.+).>' cannot be located in parent view", new_e)
                    if m and m.group(1) == new_expr:
                        continue
                    # it seems that we fixed this issue, but still have another, lets continue...
                    # WARNING: the call below could cause infinite recursion but is needed in order to fix
                    #          views that have more than one issue...
                    return heuristic_fixes(cr, view, check, new_e, tried_anchors)

        return False

    arch = etree.fromstring(view.arch_db)

    # Handle removed field that is being re-added or modified via xpath
    m = re.search("Field `(.+)` does not exist", e)
    if m:
        field_name = m.group(1)
        elems = arch.xpath("//xpath/field[@name='{}']".format(field_name))
        if not elems:
            return False
        if not field_change(view, field_name):
            # this field was not changed during upgrade, let this view fail
            return False
        new_name = field_new_name(view, field_name)
        for field_elem in elems:
            if new_name:
                _logger.info("Field %r was renamed to %r", field_name, new_name)
                field_elem.attrib["name"] = new_name
                continue
            parent = field_elem.getparent()
            parent.remove(field_elem)
            _logger.info(
                "The field %s was removed during the upgrade, removing %r from the arch", pp_xml_elem(field_elem)
            )
            if parent.tag == "xpath" and len(parent) == 0 and not parent.text.strip():
                # remove the xpath elem if empty
                parent.getparent().remove(parent)
                _logger.info("Removed empty xpath element %r", pp_xml_elem(parent))
        save_arch(view, arch)
        return heuristic_fixes(cr, view, check, check())

    # Element '<field name="name">' cannot be located in parent view
    m = re.search("Element '<field name=.(.+).>' cannot be located in parent view", e)
    if m:
        name = m.group(1)
        elems = arch.xpath("//field[@name='{}']".format(name))
        if not elems:
            _logger.info("Couldn't find <field> with name=%r in arch", name)
            return False
        elem = elems[0]
        # Transform this into an xpath element and rerun the check. This effectively defers
        # the handling of this error to the xpath section below
        orig_pp = pp_xml_elem(elem)
        elem.tag = "xpath"
        elem.attrib["expr"] = "//field[@name='{}']".format(name)
        del elem.attrib["name"]
        save_arch(view, arch)
        _logger.info("Replaced %r by %r", orig_pp, pp_xml_elem(elem))
        return heuristic_fixes(cr, view, check, check())

    # Handle xpaths that cannot be anchored
    m = re.search("Element '<xpath expr=.(.+).>' cannot be located in parent view", e)
    if m:
        expr = m.group(1)
        for _expr in (expr, unescape(expr)):
            xpath_elem = find_xpath_elem(arch, _expr)
            if xpath_elem is not None:
                break
        else:
            _logger.info("Couldn't find <xpath expr=%r> maybe it has some escaped characters.", m.group(1))
            return False
        expr = unescape(expr)  # unescape needed for '<xpath expr="//field[@name=&#39;price&#39;]">'
        if xpath_elem.getparent() is None:
            # wrap arch in <data> to always have a parent
            old_arch = arch
            arch = etree.Element("data")
            arch.append(old_arch)
            assert xpath_elem.getparent().tag == "data"

        # Extract the field name to know what happened to it
        m = re.search(r"""@name=("|')([A-Za-z_]+)\1""", expr)
        field_name = m.group(2) if m else None
        new_name = field_new_name(view, field_name)
        if new_name:
            new_expr = re.sub("@name=.{}.".format(field_name), "@name='{}'".format(new_name), expr)
            _logger.info("Field %r was renamed to %r", field_name, new_name)
            xpath_elem.set("expr", new_expr)
            save_arch(view, arch)
            return heuristic_fixes(cr, view, check, check())

        # If we only change attributes or remove the field from the view
        # then don't do it anymore since we cannot find the field anyway
        if xpath_elem.attrib["position"] == "attributes" or (
            xpath_elem.attrib["position"] == "replace" and len(xpath_elem) == 0
        ):
            _logger.info(
                "Removing %s from the arch since it only replaces or change attributes from an invalid field.",
                pp_xml_elem(xpath_elem),
            )
            xpath_elem.getparent().remove(xpath_elem)
            save_arch(view, arch)
            return heuristic_fixes(cr, view, check, check())

        # A replace xpath could be the cause of failure for children/sibling views
        # Ex: a standard view uses an anchor to a field that is removed by a custom view.
        # We test here if changing the xpath from replace to position after solves the
        # original error. If not, then fail
        if xpath_elem.attrib["position"] == "replace":
            _logger.info("Changing 'replace' position on %s", pp_xml_elem(xpath_elem))
            xpath_elem.set("position", "after")

            # check first that the field  was not renamed/removed during the upgrade
            if not field_change(view, field_name):
                save_arch(view, arch)
                new_e = check()
                if e == new_e:
                    # We are failing on same error, thus we assume the field is gone
                    # from the parent views. What rest to do is to find another anchor.
                    return heuristic_fixes(cr, view, check, new_e)

                # We don't fail anymore on the same error, but since we were replacing a field,
                # at least we could try to hide it now
                aelem = etree.SubElement(
                    xpath_elem.getparent(),
                    "xpath",
                    expr=xpath_elem.attrib["expr"],
                    position="attributes",
                )
                etree.SubElement(aelem, "attribute", name="invisible").text = "1"
                save_arch(view, arch)
                if new_e != check():
                    # We got a different error, this is not supposed to happen since we
                    # just hid the field
                    _logger.info(
                        "Unexpected error while hidding, instead of replacing, field %r:\n%s\n", field_name, new_e
                    )
                    return False
                return heuristic_fixes(cr, view, check, check())

        # Locate missing anchor on parent's backup archs
        for parent_arch_bk in get_parent_arch_bks(cr, view):
            if update_anchor(view, arch, xpath_elem, parent_arch_bk):
                return True

    return False


def _upgrade_fix_views(fix_view, root_view):
    """
    Try to fix this view. First, disable all its children and check if it still fails:
    * If the view fails, restore its arch from fs for standard views, else try to fix the custom view by
    following some heuristics (only if ODOO_MIG_TRY_FIX_VIEWS is true).
    * If the view succeeds with all children disabled, then enable the children one by one. Once a child makes
    the view fail, try to fix the child recursively.

    If a custom view cannot be fixed, then disable it.
    """

    def view_data(view, md):
        data = {
            "id": view.id,
            "name": view.name,
            "model": view.model,
            "inherit_id": view.inherit_id,
            "arch_fs": view.arch_fs,
        }
        if md:
            data.update({"module": md.module, "xml_id": "{}.{}".format(md.module, md.name)})
        return data

    def restore_from_file(view, md):
        def resolve_external_ids(arch_fs, module):
            xmlid_to_res_id = (
                fix_view.env["ir.model.data"]._xmlid_to_res_id
                if hasattr(fix_view.env["ir.model.data"], "_xmlid_to_res_id")
                else fix_view.env["ir.model.data"].xmlid_to_res_id
            )

            def replacer(m):
                xmlid = m.group("xmlid")
                if "." not in xmlid:
                    xmlid = "%s.%s" % (module, xmlid)
                return m.group("prefix") + str(xmlid_to_res_id(xmlid))

            return re.sub(r"(?P<prefix>[^%])%\((?P<xmlid>.*?)\)[ds]", replacer, arch_fs)

        arch_fs_fullpath = (
            get_resource_path(*view.arch_fs.split("/"))
            if md.module != "test_upg"
            else os.path.dirname(os.path.abspath(__file__)) + "/{}".format(view.arch_fs)
        )
        arch_db = get_view_arch_from_file(arch_fs_fullpath, view.xml_id)
        if not arch_fs_fullpath or not arch_db:
            _logger.warning(
                "The standard view `%s.%s` was set to `noupdate` and caused validation issues.\n"
                "Its original definition couldn't be recovered from the file system. Maybe it "
                "was moved or does not exist anymore.",
                md.module,
                md.name,
            )
            return

        view_copy = view.with_context(_upgrade_fix_views=True).copy(
            {"active": False, "name": "%s (Copy created during upgrade)" % view.name}
        )
        view.arch_db = to_text(resolve_external_ids(arch_db, md.module).replace("%%", "%"))

        # Mark the view as it was loaded with its XML data file.
        # Otherwise it will be deleted in _process_end
        if util.version_gte("saas~11.5"):
            fix_view.pool.loaded_xmlids.add("%s.%s" % (md.module, md.name))
        else:
            fix_view.pool.model_data_reference_ids[(md.module, md.name)] = (view._name, view.id)

        info = view_data(view, md)
        info["copy_id"] = view_copy.id

        util.add_to_migration_reports(info, "Overridden views")

        _logger.log(
            # info on CI since this is due to test data
            logging.INFO if md.module == "test_upg" else logging.WARNING,
            "The standard view `%s.%s` was set to `noupdate` and caused validation issues.\n"
            "Resetting its arch and noupdate flag for the migration ...\n",
            md.module,
            md.name,
        )

    def disable(view, md, reactivate_children):
        view.active = False
        act_window = fix_view.env["ir.actions.act_window"]
        act_window.search([("view_id", "=", view.id)]).write({"view_id": False})
        act_window.search([("search_view_id", "=", view.id)]).write({"search_view_id": False})
        fix_view.env["ir.actions.act_window.view"].search([("view_id", "=", view.id)]).unlink()

        # reactivate any disabled inheriting view
        for child in reactivate_children:
            child.active = True

        util.add_to_migration_reports(view_data(view, md), "Disabled views")
        _logger.log(
            # info on CI since this is due to test data
            logging.INFO if util.on_CI() else logging.WARNING,
            "The custom view `%s` (ID: %s, Inherit: %s, Model: %s) caused validation issues.\n"
            "Disabling it for the migration ...\n",
            view.name,
            view.id,
            view.inherit_id.id,
            view.model,
        )

    def check():
        # Check from root view and return the exception representation
        e = None
        with mute_logger("odoo.addons.base.ir.ir_ui_view", "odoo.addons.base.models.ir_ui_view"):
            try:
                super(IrUiView, root_view.with_context(lang="en_US"))._check_xml()
            except Exception as _e:
                e = str(_e)
        return e

    # 1. Disable all children
    children = fix_view.inherit_children_ids
    for child in children:
        child.active = False

    md = fix_view.model_data_id
    e = check()
    if e is not None:
        # Try to fix this view:
        #  * If standard restore from fs
        #  * If not standard:
        #    a. Try some heuristics based on the exception
        #    b. If still failing, disable the view
        if md and md.module in get_standard_modules(fix_view):
            # Standard view
            if md.noupdate and fix_view.arch_fs:
                md.noupdate = False
                restore_from_file(fix_view, md)
            # Note: even if restoring from fs, a standard view could still fail due to a custom sibling
            # removing an anchor field. We'll attempt to fix that when validating the custom sibling
        else:
            # Custom view
            if not ODOO_MIG_TRY_FIX_VIEWS:
                disable(fix_view, md, children)
                return True
            arch_orig = fix_view.arch
            if not heuristic_fixes(fix_view._cr, fix_view, check, e):
                # arch may have been changed by heuristic_fixes, restore it
                fix_view.arch = arch_orig
                disable(fix_view, md, children)
                return True
            else:
                # Only log a warning for non-CI upgrades as this situation occurs due to test data.
                # This is expected and should not mark the build as failed.
                _logger.log(
                    logging.INFO if util.on_CI() else logging.WARNING,
                    "The custom view `%s` (ID: %s, Inherit: %s, Model: %s) caused validation issues.\n"
                    "It was automatically adapted from:\n%sto:\n%s",
                    fix_view.name,
                    fix_view.id,
                    fix_view.inherit_id.id,
                    fix_view.model,
                    pp_xml_str(arch_orig),
                    pp_xml_str(fix_view.arch),
                )

    # Let's try to activate children one by one
    # If a child fails we then recursively fix it
    standard_children = filter(is_standard_view, children)
    custom_children = filterfalse(is_standard_view, children)
    has_error = []
    for child in itertools.chain(standard_children, custom_children):
        child.active = True
        if check() is not None:
            if not _upgrade_fix_views(child, root_view):
                # This view will fail since a failing child can't be fixed
                # we continue to the rest of the children to check them more
                has_error.append(child)
                child.active = False

    # We need to ensure that all children get activated again
    for child in has_error:
        child.active = True

    if check() is not None:
        # We still need to try restoring this standard view since it's in error
        # and we already tried to fix all its children
        if md and md.noupdate and md.module and fix_view.arch_fs:
            md.noupdate = False
            restore_from_file(fix_view, md)

    # If a view is mode="primary" but inherits from a standard view, it may
    # be that the standard parent (or a farther ancestor) is broken
    # and needs to be restored. We don't check whether the view or its parent
    # is standard, as custom cases should already be handled before.
    if check() is not None and fix_view.mode == "primary":
        parent = fix_view.inherit_id
        while parent:
            md_parent = parent.model_data_id
            if md_parent and md_parent.noupdate and md_parent.module in get_standard_modules(fix_view):
                md_parent.noupdate = False
                restore_from_file(parent, md_parent)
                if check() is None:
                    break
            # If parent was still in updateable or the
            # view still fails we continue to the ancestors
            parent = parent.inherit_id

    # Final check, even if has_error
    return check() is None


class IrUiView(models.Model):
    _inherit = "ir.ui.view"
    _module = "base"

    if util.version_gte("10.0"):

        def _check_xml(self):
            # Do not validate views during the upgrade. All views will be validated at once after upgrade.
            if not self.env.context.get("_upgrade_validate_views"):
                return True
            for record in self.with_context(_migrate_enable_studio_check=True):
                try:
                    super(IrUiView, record)._check_xml()
                except Exception:
                    if not _upgrade_fix_views(record, record):
                        raise
            return True

        def copy_translations(old, new, *args, **kwargs):  # noqa: B902
            # Do not copy translations when restoring view from fs
            if old.env.context.get("_upgrade_fix_views"):
                return
            return super(IrUiView, old).copy_translations(new, *args, **kwargs)

        @api.model
        def _register_hook(self):
            """
            Validate all views, whether custom or not,
            with the fields coming from custom modules loaded as manual fields.
            """
            super(IrUiView, self)._register_hook()
            origin_validators = dict(_validators)
            dummy_validators = dict.fromkeys(_validators, [lambda *args, **kwargs: True])
            query = """
                       SELECT v.id,
                              COALESCE(md.module IN %s, False)
                         FROM ir_ui_view v
                    LEFT JOIN ir_model_data md
                           ON md.model = 'ir.ui.view'
                          AND md.res_id = v.id
                        WHERE v.active
                    """
            self._cr.execute(query, [tuple(get_standard_modules(self))])
            res = self._cr.fetchall()
            standard_ids = {r[0] for r in res if r[1]}
            STANDARD_IDS.update(standard_ids)
            all_ids = {r[0] for r in res}

            def custom_view_in_tree(view):
                # Starting from the first primary ancestor, check the views' tree for custom views
                # Return true if at least one view is custom
                if view.mode == "primary" and view.id not in standard_ids:
                    return True
                while view.mode != "primary" and view.inherit_id:
                    view = view.inherit_id
                q = """
                    WITH RECURSIVE view_tree AS (
                            -- init with first level children
                            SELECT id
                              FROM ir_ui_view
                             WHERE inherit_id = %s
                               AND mode = 'extension'
                               AND active

                             UNION
                            -- add descendants
                            SELECT v.id
                              FROM ir_ui_view v
                              JOIN view_tree vt
                                ON v.inherit_id = vt.id
                             WHERE v.mode = 'extension'
                               AND v.active
                           )
                    SELECT id FROM view_tree
                    """
                self._cr.execute(q, [view.id])
                ids = {r[0] for r in self._cr.fetchall()}
                return not (ids <= standard_ids)

            def validate_view(view, is_custom_module):
                _validators.update(dummy_validators if is_custom_module else origin_validators)
                view = view.with_context(
                    _upgrade_validate_views=True,
                    load_all_views=is_custom_module,
                    _upgrade_custom_modules=is_custom_module,
                )
                if view.model not in self.env.registry:
                    return
                try:
                    view._check_xml()
                except Exception:
                    _logger.exception("Invalid custom view %s for model %s", view.xml_id or view.id, view.model)

            with util.custom_module_field_as_manual(self.env, do_flush=True):
                views_to_check = self.search([("id", "in", tuple(all_ids)), ("inherit_id", "=", False)])
                children = views_to_check.mapped("inherit_children_ids")
                while children:
                    views_to_check |= children
                    children = children.mapped("inherit_children_ids")
                for view in views_to_check:
                    if view.id in standard_ids:
                        validate_view(view, False)  # standard validators
                    if custom_view_in_tree(view):
                        validate_view(view, True)  # dummy validators

            _validators.update(origin_validators)

            self._cr.execute("DROP TABLE ir_ui_view_data_backup")

            if util.ENVIRON.get("IGNORED_IR_UI_VIEW_CHECK_GROUPS"):
                views = util.ENVIRON["IGNORED_IR_UI_VIEW_CHECK_GROUPS"]
                util.add_to_migration_reports(
                    """
                    <details>
                        <summary>
                            <p>
                                %sQWeb views cannot have 'Groups' defined on the record.
                                Instead, use the 'groups' attributes inside the view definition.
                            </p>
                            <p>
                                QWeb views are cached in memory and the cache does not depend on the user or their groups.
                                This means that if a user having the group defined on the view access the view first,
                                and then a second user without the group access the same view,
                                this second user will see the view as the first user,
                                as if they were part of the restricting group.
                                However, if the group is set in the view architecture itself with the `groups=` attribute
                                rather than on the `group_ids` field of the `ir.ui.view` record, this will work as expected.
                            </p>
                            <p>
                                The following QWeb views have groups (`groups_id`) defined on their record rather
                                than in the view architecture itself, and therefore deserve your attention:
                            </p>
                        </summary>
                        <ul>%s</ul>
                    </details>
                """
                    % (
                        "Inherited " if util.version_gte("14.0") else "",
                        "".join(
                            "<li>%s</li>"
                            % util.get_anchor_link_to_record("ir.ui.view", view_id, view_xml_id or view_name)
                            for view_id, view_xml_id, view_name, in views
                        ),
                    ),
                    "Views",
                    format="html",
                )

        if not util.on_CI():

            @api.constrains("type", "groups_id", "inherit_id")
            def _check_groups(self):
                try:
                    return super(IrUiView, self)._check_groups()
                except Exception:
                    for view in self:
                        _logger.warning(
                            "The `_check_groups` constraint has been explicitely ignored "
                            "for the view #%s during the upgrade.",
                            view.id,
                        )
                        util.ENVIRON.setdefault("IGNORED_IR_UI_VIEW_CHECK_GROUPS", []).append(
                            (view.id, view.name, view.xml_id)
                        )

    if util.version_gte("saas~11.5"):
        # Force the update of arch_fs and the view validation even if the view has been set to noupdate.
        # From saas-11.5, `_update` of ir.model.data is deprecated and replaced by _load_records on each models
        def _load_records(self, data_list, update=False):
            xml_ids = [data["xml_id"] for data in data_list if data.get("xml_id")]
            force_check_views = self.env["ir.ui.view"]
            for xml_id, row in zip(xml_ids, self.env["ir.model.data"]._lookup_xmlids(xml_ids, self)):
                d_id, d_module, d_name, d_model, d_res_id, d_noupdate, r_id = row
                if d_model == "theme.ir.ui.view":
                    # Since odoo/odoo#104094 (odoo/odoo@b89b70cc) we do not allow updating a model while loading records
                    # Given github.com/odoo/odoo/blob/d335052223e6b2a8cb6b3ae98c996f6874a2d5e5/odoo/tools/convert.py#L598-L601
                    # some custom themes (**wrongly** using an external standard xmlid) override the model of a standard
                    # template from ir.ui.view to theme.ir.ui.view, this causes issues when loading the standard view.
                    util.remove_record(self.env.cr, xml_id)
                    continue

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

    if util.version_gte("12.0"):

        def _load_records_write(self, values):
            # https://github.com/odoo/odoo/blob/c53081f10befd4f1c98e46a450ed3bc71a6246ed/odoo/fields.py#L507
            values.setdefault("priority", self._fields["priority"].default(self))
            return super()._load_records_write(values)

    if util.version_gte("saas~13.1"):

        def unlink(self):
            for view in self:
                if view.xml_id:
                    if "view:%s" % (view.xml_id) in os.environ.get("suppress_upgrade_warnings", "").split(","):
                        _logger.log(25, "View unlink %s explicitly ignored", (view.xml_id))
                    else:
                        _logger.critical("It looks like you forgot to call `util.remove_view(cr, %r)`", view.xml_id)

            return super().unlink()

        def _validate_tag_button(self, *args, **kwargs):
            if self.env.context.get("_upgrade_custom_modules"):
                return
            return super()._validate_tag_button(*args, **kwargs)

        def _validate_tag_label(self, *args, **kwargs):
            if self.env.context.get("_upgrade_custom_modules"):
                return
            return super()._validate_tag_label(*args, **kwargs)
