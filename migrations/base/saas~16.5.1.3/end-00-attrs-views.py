# -*- coding: utf-8 -*-
import ast
import contextlib
import re
import logging
import itertools
import os
from lxml import etree
from psycopg2.extras import Json as PsycopgJson
from collections import defaultdict

import odoo.modules
from odoo.exceptions import ValidationError
from odoo.upgrade import util
from odoo.tools import safe_eval, locate_node, apply_inheritance_specs, mute_logger
from odoo.tools.safe_eval import _BUILTINS
from odoo.tools.misc import unique, str2bool
from odoo.tools.view_validation import get_expression_field_names, _get_expression_contextual_values, get_domain_value_names
from odoo.osv.expression import (
    DOMAIN_OPERATORS,
    TERM_OPERATORS, AND_OPERATOR, OR_OPERATOR, NOT_OPERATOR,
    normalize_domain,
    distribute_not,
    TRUE_LEAF, FALSE_LEAF,
)

_logger = logging.getLogger(__name__)

VALID_TERM_OPERATORS = TERM_OPERATORS + ("<>", "==")
AST_OP_TO_STR = {
    ast.Eq: "==",
    ast.NotEq: "!=",
    ast.Lt: "<",
    ast.LtE: "<=",
    ast.Gt: ">",
    ast.GtE: ">=",
    ast.Is: "is",
    ast.IsNot: "is not",
    ast.In: "in",
    ast.NotIn: "not in",
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
    ast.FloorDiv: "//",
    ast.Mod: "%",
    ast.Pow: "^",
}

all_failed_nodes = defaultdict(list)

class InvalidDomainError(ValueError):
    """Domain can contain only '!', '&', '|', tuples or expression whose returns boolean"""


def migrate(cr, version):
    env = util.orm.env(cr)
    View = env['ir.ui.view'].sudo()
    Data = env['ir.model.data'].sudo()

    standard_modules = set(odoo.modules.get_modules()) - {"modules.get_modules()"}

    cr.execute("""
        SELECT
            v.id as rec_id,
            d.module as module,
            d.name as name,
            v.name as view_name,
            v.model as rec_model,
            v.type as view_type,
            v.arch_db as arch_db,
            v.inherit_id as inherit_id,
            v.mode as mode,
            v.priority as priority,
            v.active as active
        FROM ir_ui_view v
        LEFT JOIN ir_model_data d
        ON d.model = 'ir.ui.view' AND d.res_id = v.id
        WHERE v.type in ('kanban', 'tree', 'form', 'calendar', 'setting', 'search')
        ORDER BY v.priority, v.id
        """)

    # apply inherit order for all views
    # Example:
    #         1         priority: 10
    #       /   \
    #      2     3      priority: 10, 10
    #     / \   / \
    #    4   5 6   7    priority: 10, 20, 10, 1
    #
    # order: 1, 2, 4, 5, 3, 7, 6
    #
    views = cr.fetchall()
    dict_views = {view[0]: view for view in views}
    order = {}
    def define_order(view):
        rec_id = view[0]
        if rec_id not in order:
            inherit_order = (view[8], view[9], rec_id)  # (mode, priority, rec_id)
            parent = dict_views.get(view[7])  # inherit_id
            if parent:
                inherit_order = define_order(parent) + inherit_order
            order[rec_id] = inherit_order
        return order[rec_id]
    views.sort(key=define_order)

    # disable all view, reactivated during their conversion
    cr.execute("""
        UPDATE ir_ui_view
        SET active=False
        WHERE type in ('kanban', 'tree', 'form', 'calendar', 'setting', 'search')
        """)
    View.invalidate_model(['active'])
    env.registry.clear_cache('templates')

    updated = 0

    for rec_id, module, name, view_name, rec_model, view_type, arch_db, inherit_id, _mode, _priority, active in views:
        changed = False
        orig_ref = f'{rec_id} ({module}.{name})' if name else f'{rec_id} ({view_name})'

        try:
            model = env[rec_model]
        except KeyError:
            # Model is custom or has been removed.
            _logger.info(
                "Unknown model %s. The <field> modifiers may be incompletely converted. %s",
                rec_model, orig_ref)
            model = None

        for lang, arch in arch_db.items():
            ref = orig_ref + f" lang={lang}"
            inherited_root = None
            if inherit_id:
                # load inherited arch
                try:
                    inherit = View.with_context(lang=lang, load_all_views=True).browse(inherit_id)
                    inherited_root = inherit._get_combined_arch()
                except Exception as error:
                    _logger.log(logging.ERROR if module in standard_modules else logging.WARNING,
                        'Can not load inherited view ir.ui.view(id={%s}) to adapt %s\n%s', inherit_id, ref, error)
                    inherited_root = False  # must not be None, used later

            try:
                head = False
                added_data = False
                arch = arch.strip()
                if arch.startswith('<?'):
                    head, arch = arch.split('\n', 1)
                if not arch.startswith('<data>'):
                    added_data = True
                    arch = f'<data>{arch}</data>'
                root = etree.fromstring(arch)
                arch_result, has_changes = convert_template_modifiers(env, rec_id, arch, root, model, view_type, ref, inherited_root=inherited_root)
                changed = changed or has_changes
                if added_data:
                    arch_result = arch_result[6:-7]
                if head:
                    arch_result = head + arch_result
                arch_db[lang] = arch_result

                if changed and module in standard_modules:
                    # TODO: replace this log info by log error when upgrade is fixed (actually some view became no-update from upgrade)
                    _logger.info('Invalid modifiers adapted in standard view %s', ref)

            except ValueError as error:
                _logger.error('Can not adapt the view %s\n%s', ref, error)
                continue

        if changed:
            updated += 1
            cr.execute("""
                UPDATE ir_ui_view
                SET arch_db=%(arch_db)s,
                    active=%(active)s
                WHERE id=%(id)s
                """, {'arch_db': PsycopgJson(arch_db), 'active': active, 'id': rec_id})
            View.browse(rec_id).invalidate_recordset(['arch_db', 'active'])
            env.registry.clear_cache('templates')
        elif active:
            # re-activate the treated view if needed
            cr.execute("UPDATE ir_ui_view SET active=true WHERE id=%(id)s", {'id': rec_id})
            View.browse(rec_id).invalidate_recordset(['active'])
            env.registry.clear_cache('templates')

    fail_nb = 0
    for rec_id, fail in all_failed_nodes.items():
        arch_db = dict_views[rec_id][6]
        for placeholder, new_spec_xml in fail:
            fail_nb += 1
            arch_db = {
                lang: arch.replace(placeholder, new_spec_xml) for lang, arch in arch_db.items()
            }
        cr.execute("""
            UPDATE ir_ui_view
            SET arch_db=%(arch_db)s
            WHERE id=%(id)s
            """, {'arch_db': PsycopgJson(arch_db), 'id': rec_id})
        View.browse(rec_id).invalidate_recordset(['arch_db', 'active'])
        env.registry.clear_cache('templates')

    _logger.info('%s/%s views have been updated to adapt modifier syntax (invisible, required, readonly) (error: %s)', updated, len(views), fail_nb)


#######################################################################


def convert_template_modifiers(env, rec_id, arch, root, rec_model, view_type, ref, inherited_root=None):
    """Convert old syntax (attrs, states...) into new modifiers syntax"""
    result = arch
    updated = False

    if not arch.startswith('<data>'):
        raise ValueError(f'Wrong formating for view conversion. Arch must be wrapped with <data>: {ref!r}\n{arch}')

    if inherited_root is None:  # this is why it must be False
        result, updated = convert_basic_view(arch, root, env, rec_model, view_type, ref)
    else:
        result, updated = convert_inherit_view(rec_id, arch, root, env, rec_model, view_type, ref, inherited_root)

    if not result.startswith('<data>'):
        raise ValueError(f'View conversion failed. Result should had been wrapped with <data>: {ref!r}\n{result}')
    root_result = etree.fromstring(result.encode())

    # Check for incomplete conversion, those attributes should had been removed by
    # convert_basic_view and convert_inherit_view. In case there are some left
    # just log an error but keep the converted view in the database/file.
    for item in root_result.findall('.//attribute[@name="states"]'):
        xml = etree.tostring(item, encoding='unicode')
        _logger.error('Incomplete view conversion ("states"): %r\n%s', ref, xml)
    for item in root_result.findall('.//attribute[@name="attrs"]'):
        xml = etree.tostring(item, encoding='unicode')
        _logger.error('Incomplete view conversion ("attrs"): %r\n%s', ref, xml)
    for item in root_result.findall('.//*[@attrs]'):
        xml = etree.tostring(item, encoding='unicode')
        _logger.error('Incomplete view conversion ("attrs"): %r\n%s', ref, xml)
    for item in root_result.findall('.//*[@states]'):
        xml = etree.tostring(item, encoding='unicode')
        _logger.error('Incomplete view conversion ("states"): %r\n%s', ref, xml)

    return result, updated

def convert_basic_view(arch, root, env, model, view_type, ref):
    updated_nodes, _analysed_nodes = convert_node_modifiers_inplace(root, env, model, view_type, ref)
    if not updated_nodes:
        return arch, False
    return replace_and_keep_indent(root, arch, ref), True

def convert_inherit_view(rec_id, arch, root, env, model, view_type, ref, inherited_root):
    updated = False
    result = arch

    def get_target(spec):
        target_node = None

        try:
            with mute_logger("odoo.tools.template_inheritance"):
                target_node = locate_node(inherited_root, spec)
                # target can be None without error
        except Exception:
            pass

        if target_node is None:
            clone = etree.tostring(etree.Element(spec.tag, spec.attrib), encoding='unicode')
            _logger.info('Target not found for %s with xpath: %s', ref, clone)
            return None, view_type, model

        parent_view_type = view_type
        target_model = model
        # subview and groupby in tree view
        parent_f_names = [p.get('name') for p in target_node.iterancestors() if p.tag in ( 'field', 'groupby')]

        for p in target_node.iterancestors():
            if p.tag in ('groupby', 'header'):
                # in tree view
                parent_view_type = 'form'
                break
            elif p.tag in ('tree', 'form', 'setting'):
                parent_view_type = p.tag
                break

        for name in reversed(parent_f_names):
            try:
                field = target_model._fields[name]
                target_model = env[field.comodel_name]
            except KeyError:
                # Model is custom or had been removed. Can convert view without using field python states
                if name in target_model._fields:
                    _logger.warning("Unknown model %s. The <field> modifiers may be incompletely converted. %s", target_model._fields[name].comodel_name, ref)
                else:
                    _logger.warning("Unknown field %s on model %s. The <field> modifiers may be incompletely converted. %s", name, target_model, ref)
                target_model = None
                break

        return target_node, parent_view_type, target_model

    specs = []
    for spec in root:
        if isinstance(spec.tag, str):
            if spec.tag == 'data':
                specs.extend(c for c in spec)
            else:
                specs.append(spec)

    for spec in specs:
        spec_updated = False
        spec_xml = get_targeted_xml_content(spec, result, ref)

        if spec.get('position') == 'attributes':
            target_node, parent_view_type, target_model = get_target(spec)
            spec_updated = convert_inherit_attributes_inplace(spec, target_node, parent_view_type)
            xml = etree.tostring(spec, pretty_print=True, encoding='unicode').strip()
        else:
            _target_node, parent_view_type, target_model = get_target(spec)
            spec_updated = convert_node_modifiers_inplace(spec, env, target_model, parent_view_type, ref)[0]
            xml = replace_and_keep_indent(spec, spec_xml, ref)

        try:
            with mute_logger("odoo.tools.template_inheritance"):
                inherited_root = apply_inheritance_specs(inherited_root, etree.fromstring(xml))
        except (ValueError, etree.XPathSyntaxError, ValidationError) as error:
            spec_updated = True
            _logger.info('Can not apply inheritance: %s\nPath: %r\n%s', ref, xml.split('>', 1)[0] + '>', error)
            # To avoid error: Comment may not contain '--' or end with '-'
            placeholder = etree.Element('xpath', expr='.', id=f'__upgrade_attribute_fail__ {len(all_failed_nodes)}')
            placeholder_xml = etree.tostring(placeholder, encoding='unicode')
            spec.getparent().replace(spec, placeholder)
            all_failed_nodes[rec_id].append((placeholder_xml, xml))
            xml = placeholder_xml

        if spec_updated:
            updated = True
            if spec_xml not in result:
                _logger.error('Wrong targetting, can not apply inheritance: %s\nPath: %r', ref, xml.split('>', 1)[0] + '>')
            else:
                result = result.replace(spec_xml, xml, 1)
    return result, updated

def convert_inherit_attributes_inplace(spec, target_node, view_type):
    """
    convert inherit with <attribute name="attrs"> + <attribute name="invisible">
    The conversion is different if attrs and invisible/readonly/required are modified.
    (can replace attributes, or use separator " or " to combine with previous)

    migration is idempotent, this eg stay unchanged:
        <attribute name="invisible">(aaa)</invisible>
        <attribute name="invisible">0</attribute>
        <attribute name="invisible">1</attribute>
        <attribute name="invisible" add="context.get('aaa')" separator=" or "/>
    """

    migrated = False
    has_change = False
    items = {}
    to_remove = set()
    node = None
    for attr in ('attrs', 'column_invisible', 'invisible', 'readonly', 'required'):
        nnode = spec.find(f'.//attribute[@name="{attr}"]')
        if nnode is None:
            continue
        to_remove.add(nnode)

        value = nnode.text and nnode.text.strip()
        if value not in ('True', 'False', '0', '1'):
            node = nnode
        if nnode.get('separator') or (value and value[0] == '('):
            # previously migrate
            migrated = True
            break
        if attr == 'attrs':
            has_change = True
            try:
                value = value and ast.literal_eval(value) or {'invisible': '', 'readonly': '', 'required': ''}
            except Exception as error:
                raise ValueError(f'Can not convert "attrs": {value!r}') from error
        elif (attr == 'invisible' and view_type == 'tree' and 'column_invisible' not in items
             and (value in ('0', '1', 'True', 'False')
                  or (value.startswith('context') and ' or ' not in value and ' and ' not in value))):
           attr = 'column_invisible'
        items[attr] = value

    if node is None or not items or migrated:
        return has_change

    index = spec.index(node)
    is_last = spec[-1] == node

    domain_attrs = items.pop('attrs', {})
    all_attrs = list((set(items) | set(domain_attrs)))
    all_attrs.sort()

    i = len(all_attrs)
    next_xml = ''
    for attr in all_attrs:
        value = items.get(attr)
        domain = domain_attrs.get(attr, '')
        attr_value = domain_to_expression(domain) if isinstance(domain, list) else str(domain)

        i -= 1
        elem = etree.Element('attribute', {'name': attr})
        if i or not is_last:
            elem.tail = spec.text
        else:
            elem.tail = spec[-1].tail
            spec[-1].tail = spec.text

        if value and attr_value:
            has_change = True
            # replace whole expression
            if value in ('False', '0'):
                elem.text = attr_value
            elif value in ('True', '1'):
                elem.text = value
            else:
                elem.text = f'({value}) or ({attr_value})'
        else:
            inherited_value = target_node.get(attr) if target_node is not None else None
            inherited_context = _get_expression_contextual_values(ast.parse(inherited_value.strip(), mode='eval').body) if inherited_value else set()
            res_value = value or attr_value or 'False'

            if inherited_context:
                # replace whole expression if replace record value by record value, or context/parent by context/parent
                # <field invisible="context.get('a')"/>
                # is replaced
                #
                # <field attrs="{'invisible': [('b', '=', 1)]}"/> => <field invisible="b == 1"/>
                # will be combined
                #
                # <field invisible="context.get('a')" attrs="{'invisible': [('b', '=', 1)]}"/>  => <field invisible="context.get('a') or b == 1"/>
                # logged because human control is necessary

                context = _get_expression_contextual_values(ast.parse(f'({res_value.strip()})', mode='eval').body)

                has_record = any(True for v in context if not v.startswith('context.'))
                has_context = any(True for v in context if v.startswith('context.'))
                inherited_has_record = any(True for v in inherited_context if not v.startswith('context.'))
                inherited_has_context = any(True for v in inherited_context if v.startswith('context.'))

                has_change = True
                if has_record == inherited_has_record and has_context == inherited_has_context:
                    elem.text = res_value
                    has_change = not attr_value
                elif res_value in ('0', 'False', '1', 'True'):
                    has_change = elem.text != res_value
                    elem.text = res_value
                else:
                    elem.set('add', res_value)
                    elem.set('separator', ' or ')
                    _logger.info('The migration of attributes inheritance might not be exact: %s', etree.tostring(elem, encoding="unicode"))
            elif not value and not attr_value:
                continue
            else:
                elem.text = res_value
                if attr_value:
                    has_change = True

        spec.insert(index, elem)
        index += 1

    # remove previous node and xml
    for node in to_remove:
        spec.remove(node)

    return has_change

def convert_node_modifiers_inplace(root, env, model, view_type, ref):
    """Convert inplace old syntax (attrs, states...) into new modifiers syntax"""
    updated_nodes = set()
    analysed_nodes = set()

    def expr_to_attr(item, py_field_modifiers=None, field=None):
        if item in analysed_nodes:
            return
        analysed_nodes.add(item)

        try:
            modifiers = extract_node_modifiers(item, view_type, py_field_modifiers)
        except ValueError as error:
            if ('country_id != %(base.' in error.args[0] or
                '%(base.lu)d not in account_enabled_tax_country_ids' in error.args[0]):
                # Odoo xml file can use %(...)s ref/xmlid, this part is
                # replaced later by the record id. This code cannot be
                # parsed into a domain and convert into a expression.
                # Just skip it.
                return
            xml = etree.tostring(item, encoding='unicode')
            _logger.error("Invalid modifiers syntax: %s\nError: %s\n%s", ref, error, xml)
            return

        # apply new modifiers on item only when modified...
        for attr in ('column_invisible', 'invisible', 'readonly', 'required'):
            new_py_expr = modifiers.pop(attr, None)
            old_expr = item.attrib.get(attr)

            if (  old_expr == new_py_expr
               or (old_expr in ('1', 'True') and new_py_expr == 'True')
               or (old_expr in ('0', 'False') and new_py_expr in ('False', None))):
                continue

            if new_py_expr and (new_py_expr != 'False'
                or (attr == 'readonly' and (not field or field.readonly))
                or (attr == 'required' and (not field or field.required))):
                item.attrib[attr] = new_py_expr
                updated_nodes.add(item)
            elif old_expr:
                item.attrib.pop(attr, None)
                updated_nodes.add(item)

        # ... and remove old attributes
        if item.attrib.pop('states', None):
            updated_nodes.add(item)
        if item.attrib.pop('attrs', None):
            updated_nodes.add(item)

        # they are some modifiers left, some templates are badly storing
        # options in attrs, then they must be left as is (e.g.: studio
        # widget, name, ...)
        if modifiers:
            item.attrib['attrs'] = repr(modifiers)

    def in_subview(item):
        for p in item.iterancestors():
            if p == root:
                return False
            if p.tag in ('field', 'groupby'):
                return True

    if model is not None:
        if view_type == 'tree':
            # groupby from tree target the field as a subview (inside groupby is treated as form)
            for item in root.findall('.//groupby[@name]'):
                f_name = item.get('name')
                field = model._fields[f_name]
                updated, fnodes =  convert_node_modifiers_inplace(item, env, env[field.comodel_name], 'form', ref)
                analysed_nodes.update(fnodes)
                updated_nodes.update(updated)

        for item in root.findall('.//field[@name]'):
            if in_subview(item):
                continue

            if item in analysed_nodes:
                continue

            # in kanban view, field outside the template should not have modifiers
            if view_type == 'kanban' and item.getparent().tag == 'kanban':
                for attr in ('states', 'attrs', 'column_invisible', 'invisible', 'readonly', 'required'):
                    item.attrib.pop(attr, None)
                continue

            # shortcut for views that do not use information from the python field
            if view_type not in ('kanban', 'tree', 'form', 'setting'):
                expr_to_attr(item)
                continue

            f_name = item.get('name')

            if f_name not in model._fields:
                level = logging.WARNING
                if f"field:{model}.{f_name}" in os.environ.get("suppress_upgrade_warnings", "").split(","):
                    level = util.NEARLYWARN
                _logger.log(level, "Unknown field %r from %r, can not migrate 'states' python field attribute in view %s", f_name, model._name, ref)
                continue
            field = model._fields[f_name]

            # get subviews
            if field.comodel_name:
                for subview in item.getchildren():
                    subview_type = subview.tag if subview.tag != 'groupby' else 'form'
                    updated, fnodes = convert_node_modifiers_inplace(subview, env, env[field.comodel_name], subview_type, ref)
                    analysed_nodes.update(fnodes)
                    updated_nodes.update(updated)

            # use python field to convert view <field>
            if item.get('readonly'):
                expr_to_attr(item, field=field)
            elif field.states:
                readonly = bool(field.readonly)
                fnames = [k for k, v in field.states.items() if v[0][1] != readonly]
                if fnames:
                    fnames.sort()
                    dom = [('state', 'not in' if readonly else 'in', fnames)]
                    expr_to_attr(item, py_field_modifiers={'readonly': domain_to_expression(dom)}, field=field)
                else:
                    expr_to_attr(item)
            elif field.readonly not in (True, False):
                try:
                    readonly_expr = domain_to_expression(str(field.readonly))
                except ValueError:
                    _logger.warning("Can not convert readonly: %r", field.readonly)
                    continue
                if readonly_expr in ('0', '1'):
                    readonly_expr = str(readonly_expr == '1')
                expr_to_attr(item, py_field_modifiers={'readonly': readonly_expr}, field=field)
            else:
                expr_to_attr(item, field=field)

    # processes all elements that have not been converted
    for item in unique(itertools.chain(
            root.findall('.//*[@attrs]'),
            root.findall('.//*[@states]'),
            root.findall('.//tree/*[@invisible]'))):
        expr_to_attr(item)

    return updated_nodes, analysed_nodes

reg_comment = r'<!--(?:-(?!-)|\n|[^-])+-->'
reg_att1 = r'[a-zA-Z0-9._-]+\s*=\s*"(?:\n|[^"])*"'
reg_att2 = r"[a-zA-Z0-9._-]+\s*=\s*'(?:\n|[^'])*'"
reg_open_tag = rf'''<[a-zA-Z0-9]+(?:\s*\n|\s+{reg_att1}|\s+{reg_att2})*\s*/?>'''
reg_close_tag = r'</[a-zA-Z0-9]+\s*>'
reg_split = rf'((?:\n|[^<])*)({reg_comment}|{reg_open_tag}|{reg_close_tag})((?:\n|[^<])*)'
reg_attrs = r''' (attrs|states|invisible|column_invisible|readonly|required)=("(?:\n|[^"])*"|'(?:\n|[^'])*')'''
close_placeholder = '</XXXYXXX>'
def split_xml(arch):
    """ split xml in tags, add a close tag for each void. """
    split = list(re.findall(reg_split, arch.replace('/>', f'/>{close_placeholder}')))
    return split

def get_targeted_xml_content(spec, field_arch_content, ref):
    spec_xml  = etree.tostring(spec, encoding='unicode').strip()
    if spec_xml in field_arch_content:
        return spec_xml

    for ancestor in spec.iterancestors():
        if ancestor.tag in ('field', 'data'):
            break

    spec_index = ancestor.index(spec)

    xml = ''
    level = 0
    index = 0
    for before, tag, after in split_xml(field_arch_content):
        if index - 1 == spec_index:
            xml += before + tag + after
        if tag[1] == '/':
            level -= 1
        elif tag[1] != '!':
            level += 1
        if level == 1:
            index += 1

    if not xml:
        ValueError('Source inheritance spec not found for %s: %s', ref, spec_xml)

    return xml.replace(close_placeholder, '').strip()

def replace_and_keep_indent(element, arch, ref):
    """ Generate micro-diff from updated attributes """
    next_record = etree.tostring(element, encoding='unicode').strip()
    n_split = split_xml(next_record)
    arch = arch.strip()
    p_split = split_xml(arch)

    control = ''
    level = 0
    for i in range(max(len(p_split), len(n_split))):
        p_node = p_split[i][1]
        n_node = n_split[i][1]
        control += ''.join(p_split[i])

        if p_node[1] != '/' and p_node[1] != '!':
            level += 1

        replace_by = p_node
        if p_node != n_node:
            if p_node == close_placeholder and not n_node.startswith('</'):
                raise ValueError("Wrong split for convertion in %s\n\n---------\nSource node:  None\nCurrent node:  %s\nSource arch:  %s\nCurrent arch:  %s" % (
                    ref, n_node, arch, next_record))
            if n_node == close_placeholder and not p_node.startswith('</'):
                raise ValueError("Wrong split for convertion in %s\n\n---------\nSource node:  %s\nCurrent node:  None\nSource arch:  %s\nCurrent arch:  %s" % (
                    ref, p_node, arch, next_record))

            p_tag = re.split(r'[<>\n /]+', p_node, 2)[1]
            n_tag = re.split(r'[<>\n /]+', n_node, 2)[1]
            if p_node != close_placeholder and n_node != close_placeholder and p_tag != n_tag:
                raise ValueError("Wrong split for convertion in %s\n\n---------\nSource node:  %s\nCurrent node:  %s\nSource arch:  %s\nCurrent arch:  %s" % (
                    ref, p_node, n_node, arch, next_record))

            p_attrs = {k: v[1:-1] for k, v in re.findall(reg_attrs, p_node)}
            n_attrs = {k: v[1:-1] for k, v in re.findall(reg_attrs, n_node)}

            if p_attrs != n_attrs:
                if p_attrs:
                    key, value = p_attrs.popitem()
                    for j in p_attrs:
                        replace_by = replace_by.replace(f' {j}="{p_attrs[j]}"', '')
                    rep = ''
                    if n_attrs:
                        space = re.search(rf'(\n? +){key}=', replace_by).group(1)
                        rep = ' ' + space.join(f'{k}="{v}"' for k, v in n_attrs.items())
                    replace_by = re.sub(r""" %s=["']%s["']""" % (re.escape(key), re.escape(value)), rep, replace_by)
                    replace_by = re.sub('(?: *\n +)+(\n +)', r'\1', replace_by)
                    replace_by = re.sub('(?: *\n +)(/?>)', r'\1', replace_by)
                else:
                    rep = ''
                    if n_attrs:
                        rep = ' ' + ' '.join(f'{k}="{v}"' for k, v in n_attrs.items())
                    if p_node.endswith('/>'):
                        replace_by = replace_by[0:-2] + rep + '/>'
                    else:
                        replace_by = replace_by[0:-1] + rep + '>'

        if p_node[1] == '/':
            level -= 1

        p_split[i] = (p_split[i][0], replace_by, p_split[i][2])

    xml = ''.join(''.join(s) for s in p_split).replace(f'/>{close_placeholder}', '/>')

    control = control.replace(f'/>{close_placeholder}', '/>')

    if not control or level != 0:
        _logger.error("Wrong convertion in %s\n\n%s", ref, control)
        raise ValueError('Missing update: \n{control}')

    return xml

def extract_node_modifiers(node, view_type, py_field_modifiers=None):
    """extract the node modifiers and concat attributes (attrs, states...)"""

    modifiers = {}

    # modifiers from deprecated attrs
    # <field attrs="{'invisible': &quot;[['user_id', '=', uid]]&quot;, 'readonly': [('name', '=', 'toto')]}" .../>
    # =>
    # modfiers['invisible'] = 'user_id == uid'
    # modfiers['readonly'] = 'name == "toto"'
    attrs = ast.literal_eval(node.attrib.get("attrs", "{}")) or {}
    for modifier, val in attrs.items():
        try:
            domain = modifier_to_domain(val)
            py_expression = domain_to_expression(domain)
        except Exception as error:
            if '%' not in str(error):
                raise
            raise ValueError(f"Invalid modifier {modifier!r}: {val!r}\n{error}") from error
        modifiers[modifier] = py_expression

    # invisible modifier from deprecated states
    # <field states="draft,done" .../>
    # =>
    # modifiers['invisible'] = "state not in ('draft', 'done')"
    states = node.attrib.get('states')
    if states:
        value = tuple(states.split(","))
        if len(value) == 1:
            py_expression = f'state != {value[0]!r}'
        else:
            py_expression = f'state not in {value!r}'
        invisible = modifiers.get('invisible') or 'False'
        if invisible == 'False':
            modifiers['invisible'] = py_expression
        else:
            # only add parenthesis if necessary
            if ' and ' in py_expression or ' or ' in py_expression:
                py_expression = f'({py_expression})'
            if ' and ' in invisible or ' or ' in invisible:
                invisible = f'({invisible})'
            modifiers['invisible'] = f'{invisible} and {py_expression}'

    # extract remaining modifiers
    # <field invisible="context.get('hide')" .../>
    for modifier in ('column_invisible', 'invisible', 'readonly', 'required'):
        py_expression = node.attrib.get(modifier, '').strip()
        if not py_expression:
            if modifier not in modifiers and py_field_modifiers and py_field_modifiers.get(modifier):
                modifiers[modifier] = py_field_modifiers[modifier]
            continue

        try:
            # most (~95%) elements are 1/True/0/False
            py_expression = repr(util.str2bool(py_expression))
        except ValueError:
            # otherwise, make sure it is a valid expression
            try:
                modifier_ast = ast.parse(f'({py_expression})', mode='eval').body
                py_expression = repr(_modifier_to_domain_ast_item(modifier_ast))
            except Exception as error:
                raise ValueError(f'Invalid modifier {modifier!r}: {error}: {py_expression!r}') from None

        # Special case, must rename "invisible" to "column_invisible"
        if modifier == 'invisible' and py_expression != 'False' and not get_expression_field_names(py_expression):
            parent_view_type = view_type
            for parent in node.iterancestors():
                if parent.tag in ('tree', 'form', 'setting', 'kanban', 'calendar', 'search'):
                    parent_view_type = parent.tag
                    break
                if parent.tag in ('groupby', 'header'):  # tree view element with form view behavior
                    parent_view_type = 'form'
                    break
            if parent_view_type == 'tree':
                modifier = 'column_invisible'

        # previous_py_expr and py_expression must be OR-ed
        # first 3 cases are short circuits
        previous_py_expr = modifiers.get(modifier, 'False')
        if (previous_py_expr == 'True'               # True or ... => True
            or py_expression == 'True'):             # ... or True => True
            modifiers[modifier] = 'True'
        elif previous_py_expr == 'False':            # False or ... => ...
            modifiers[modifier] = py_expression
        elif py_expression == 'False':               # ... or False => ...
            modifiers[modifier] = previous_py_expr
        else:
            # only add parenthesis if necessary
            if ' and ' in previous_py_expr or ' or ' in previous_py_expr:
                previous_py_expr = f'({previous_py_expr})'
            modifiers[modifier] = f'{py_expression} or {previous_py_expr}'

    return modifiers

def domain_to_expression(domain):
    """Convert the given domain into a python expression"""
    domain = update_normalize_domain(domain)
    domain = distribute_not(domain)
    operators = []
    expression = []
    for leaf in reversed(domain):
        if leaf == AND_OPERATOR:
            right = expression.pop()
            if operators.pop() == OR_OPERATOR:
                right = f'({right})'
            left = expression.pop()
            if operators.pop() == OR_OPERATOR:
                left = f'({left})'
            expression.append(f'{right} and {left}')
            operators.append(leaf)
        elif leaf == OR_OPERATOR:
            right = expression.pop()
            operators.pop()
            left = expression.pop()
            operators.pop()
            expression.append(f'{right} or {left}')
            operators.append(leaf)
        elif leaf == NOT_OPERATOR:
            expr = expression.pop()
            operators.pop()
            expression.append(f'not ({expr})')
            operators.append(leaf)
        elif leaf is True or leaf is False:
            expression.append(repr(leaf))
            operators.append(None)
        elif leaf in (TRUE_LEAF, FALSE_LEAF):
            expression.append(repr(leaf is TRUE_LEAF))
            operators.append(None)
        elif isinstance(leaf, (tuple, list)):
            left, op, right = leaf
            if op == '=' or op == '==':
                if right is False or right == []:
                    expr = f'not {left}'
                elif left.endswith('_ids'):
                    expr = f'{right!r} in {left}'
                elif right is True:
                    expr = f'{left}'
                else:
                    expr = f'{left} == {right!r}'
            elif op == '!=' or op == '<>':
                if right is False or right == []:
                    expr = str(left)
                elif left.endswith('_ids'):
                    expr = f'{right!r} not in {left}'
                elif right is True:
                    expr = f'not {left}'
                else:
                    expr = f'{left} != {right!r}'
            elif op in ('<=', '<', '>', '>='):
                expr = f'{left} {op} {right!r}'
            elif op == '=?':
                expr = f'(not {right} or {left} in {right!r})'
            elif op == 'in' or op == 'not in':
                right_str = str(right)
                if right_str == '[None, False]':
                    expr = f'not ({left})'
                elif left.endswith('_ids'):
                    if right_str.startswith('[') and ',' not in right_str:
                        expr = f'{right[0]!r} {op} {left}'
                    if not right_str.startswith('[') and right_str.endswith('id'):
                        # fix wrong use of 'in' inside domain
                        expr = f'{right_str!r} {op} {left}'
                    else:
                        raise ValueError(f"Can not convert {domain!r} to python expression")
                else:
                    if right_str.startswith('[') and ',' not in right_str:
                        op = '==' if op == 'in' else '!='
                        expr = f'{left} {op} {right[0]!r}'
                    else:
                        expr = f'{left} {op} {right!r}'
            elif op == 'like' or op == 'not like':
                if isinstance(right, str):
                    part = right.split('%')
                    if len(part) == 1:
                        op = 'in' if op == 'like' else 'not in'
                        expr = f'{right!r} {op} ({left} or "")'
                    elif len(part) == 2:
                        if part[0] and part[1]:
                            expr = f'({left} or "").startswith({part[0]!r}) and ({left} or "").endswith({part[1]!r})'
                        elif part[0]:
                            expr = f'({left} or "").startswith({part[0]!r})'
                        elif part[1]:
                            expr = f'({left} or "").endswith({part[0]!r})'
                        else:
                            expr = str(left)
                        if op.startswith('not '):
                            expr = f'not ({expr})'
                    else:
                        raise ValueError(f"Can not convert {domain!r} to python expression")
                else:
                    op = 'in' if op == 'like' else 'not in'
                    expr = f'{right!r} {op} ({left} or "")'
            elif op == 'ilike' or op == 'not ilike':
                if isinstance(right, str):
                    part = right.split('%')
                    if len(part) == 1:
                        op = 'in' if op == 'ilike' else 'not in'
                        expr = f'{right!r}.lower() {op} ({left} or "").lower()'
                    elif len(part) == 2:
                        if part[0] and part[1]:
                            expr = f'({left} or "").lower().startswith({part[0]!r}) and ({left} or "").lower().endswith({part[1]!r})'
                        elif part[0]:
                            expr = f'({left} or "").lower().startswith({part[0]!r})'
                        elif part[1]:
                            expr = f'({left} or "").lower().endswith({part[0]!r})'
                        else:
                            expr = str(left)
                        if op.startswith('not '):
                            expr = f'not ({expr})'
                    else:
                        raise ValueError(f"Can not convert {domain!r} to python expression")
                else:
                    op = 'in' if op == 'like' else 'not in'
                    expr = f'{right!r}.lower() {op} ({left} or "").lower()'
            else:
                raise ValueError(f"Can not convert {domain!r} to python expression")
            expression.append(expr)
            operators.append(None)
        else:
            expression.append(repr(leaf))
            operators.append(None)

    return expression.pop()

class ContextDependentDomainItem:
    """
        Holds information about values dependent on the context.
        Attributes:
        `value`: <some info here, it's not clear>
        `contextual_values`: <info here to make it clear>
        `returns_boolean`: whether the final value resolved from the context should be a boolean
        `returns_domain`: whether the final value resolved from the context should be a valid domain

        The `str` representation for instances of this class is equivalent to the value from the context <not sure but it looks like??>.
    """
    def __init__(self, value, names, returns_boolean=False, returns_domain=False):
        self.value = value
        self.contextual_values = names
        self.returns_boolean = returns_boolean
        self.returns_domain = returns_domain
    def __str__(self):
        if self.returns_domain:
            return repr(self.value)
        return self.value
    def __repr__(self):
        return self.__str__()

def _modifier_to_domain_ast_wrap_domain(modifier_ast):
    try:
        domain_item = _modifier_to_domain_ast_item(modifier_ast, should_contain_domain=True)
    except Exception as e:
        raise ValueError(f'{e}\nExpression must returning a valid domain in all cases') from None

    if not isinstance(domain_item, ContextDependentDomainItem) or not domain_item.returns_domain:
        raise ValueError('Expression must returning a valid domain in all cases')
    return domain_item.value

def _modifier_to_domain_ast_domain(modifier_ast):
    # ['|', ('a', '=', 'b'), ('user_id', '=', uid)]

    if not isinstance(modifier_ast, ast.List):
        raise ValueError('This part must be a domain') from None

    domain = []
    for leaf in modifier_ast.elts:
        if isinstance(leaf, ast.Str) and leaf.s in DOMAIN_OPERATORS:
            # !, |, &
            domain.append(leaf.s)
        elif isinstance(leaf, ast.Constant):
            if leaf.value is True or leaf.value is False:
                domain.append(leaf.value)
            else:
                raise InvalidDomainError()
        elif isinstance(leaf, (ast.List, ast.Tuple)):
            # domain tuple
            if len(leaf.elts) != 3:
                raise InvalidDomainError()
            elif not isinstance(leaf.elts[0], ast.Constant) and not (isinstance(leaf.elts[2], ast.Constant) and leaf.elts[2].value == 1):
                raise InvalidDomainError()
            elif not isinstance(leaf.elts[1], ast.Constant):
                raise InvalidDomainError()

            left_ast, operator_ast, right_ast = leaf.elts

            operator = operator_ast.value
            if operator == '==':
                operator = '='
            elif operator == '<>':
                operator = '!='
            elif operator not in TERM_OPERATORS:
                raise InvalidDomainError()

            left = _modifier_to_domain_ast_item(left_ast)
            right = _modifier_to_domain_ast_item(right_ast)
            domain.append((left, operator, right))
        else:
            item = _modifier_to_domain_ast_item(leaf)
            domain.append(item)
            if item not in (True, False) and isinstance(item, ContextDependentDomainItem) and not item.returns_boolean:
                raise InvalidDomainError()

    return update_normalize_domain(domain)

def _modifier_to_domain_ast_item(item_ast, should_contain_domain=False, need_parenthesis=False):
    """
        Transform an item from an AST domain leaf into its values. It handles context
        dependent values by returning ContextDependentDomainItem instances. It takes
        care of all patterns allowed.

        For example an AST parsed from `[1,2,True]` will return just `[1,2,True]`.
        But `[1,2,uid]` returns `[1,2,ContextDependentDomainItem(...)]` since `uid` comes from the context.
        Similarly `[('a', '=', 1)] if context.get('b') else []` returns a `ContextDependentDomainItem(...,returns_domain=True)`
        ...

        Params:
        `should_contain_domain`: True for ... IDK?, False otherwise
        `need_parenthesis`: True for..., ...
    """
    # [('a', '=', True)]
    # True
    if isinstance(item_ast, ast.Constant):
        return item_ast.value

    # [('a', '=', 1)] if context.get('b') else []
    # [('a', '=', 1)]
    if should_contain_domain and isinstance(item_ast, ast.List):
        domain = _modifier_to_domain_ast_domain(item_ast)
        _fnames, vnames = get_domain_value_names(domain)
        return ContextDependentDomainItem(domain, vnames, returns_domain=True)

    vnames = set()  # name of contextual values (need record/env to eval the generated expresion)

    # [('obj_ids', 'in', [uid or False, 33])]
    # [uid or False, 33]
    if isinstance(item_ast, (ast.List, ast.Tuple)):
        values = []
        for item in item_ast.elts:
            value = _modifier_to_domain_ast_item(item)
            if isinstance(value, ContextDependentDomainItem):
                vnames.update(value.contextual_values)
            values.append(value)

        if isinstance(item_ast, ast.Tuple):
            values = tuple(values)

        if vnames:
            return ContextDependentDomainItem(repr(values), vnames)
        else:
            return values

    # [('a', '=', uid)]
    # uid
    if isinstance(item_ast, ast.Name):
        return ContextDependentDomainItem(item_ast.id, {item_ast.id})

    # [('a', '=', parent.b)]
    # parent.b
    if isinstance(item_ast, ast.Attribute):
        name = _modifier_to_domain_ast_item(item_ast.value, need_parenthesis=True)
        if isinstance(name, ContextDependentDomainItem):
            vnames.update(name.contextual_values)
        value = f"{name!r}.{item_ast.attr}"
        if value.startswith('parent.'):
            vnames.add(value)
        return ContextDependentDomainItem(value, vnames)

    # [('a', '=', company_ids[1])]
    # [1]
    if isinstance(item_ast, ast.Index): # deprecated python ast class for Subscript key
        return _modifier_to_domain_ast_item(item_ast.value)

    # [0:-1]
    # 0:-1
    if isinstance(item_ast, ast.Slice):
        lower = _modifier_to_domain_ast_item(item_ast.lower)
        if isinstance(lower, ContextDependentDomainItem):
            vnames.update(lower.contextual_values)

        upper = _modifier_to_domain_ast_item(item_ast.upper)
        if isinstance(upper, ContextDependentDomainItem):
            vnames.update(upper.contextual_values)

        value = f"{lower!r}:{upper!r}"
        return ContextDependentDomainItem(value, vnames)

    # [('a', '=', company_ids[1])]
    # [1]
    if isinstance(item_ast, ast.Subscript):
        name = _modifier_to_domain_ast_item(item_ast.value, need_parenthesis=True)
        if isinstance(name, ContextDependentDomainItem):
            vnames.update(name.contextual_values)

        key = _modifier_to_domain_ast_item(item_ast.slice)
        if isinstance(key, ContextDependentDomainItem):
            vnames.update(key.contextual_values)
        value = f"{name!r}[{key!r}]"

        return ContextDependentDomainItem(value, vnames)

    # [('a', '=', context.get('abc', 'default') == 'b')]
    # ==
    if isinstance(item_ast, ast.Compare):
        if len(item_ast.ops) > 1:
            raise ValueError(f"Maximum one comparison allowed: {expr}")

        left = _modifier_to_domain_ast_item(item_ast.left, need_parenthesis=True)
        if isinstance(left, ContextDependentDomainItem):
            vnames.update(left.contextual_values)

        operator = AST_OP_TO_STR[type(item_ast.ops[0])]

        right = _modifier_to_domain_ast_item(item_ast.comparators[0], need_parenthesis=True)
        if isinstance(right, ContextDependentDomainItem):
            vnames.update(right.contextual_values)

        expr = f"{left!r} {operator} {right!r}"
        return ContextDependentDomainItem(expr, vnames, returns_boolean=True)

    # [('a', '=', 1 - 3]
    # 1 - 3
    if isinstance(item_ast, ast.BinOp):
        left = _modifier_to_domain_ast_item(item_ast.left)
        if isinstance(left, ContextDependentDomainItem):
            vnames.update(left.contextual_values)

        operator = AST_OP_TO_STR[type(item_ast.op)]

        right = _modifier_to_domain_ast_item(item_ast.right)
        if isinstance(right, ContextDependentDomainItem):
            vnames.update(right.contextual_values)

        expr = f"{left!r} {operator} {right!r}"
        return ContextDependentDomainItem(expr, vnames)

    # [(1, '=', field_name and 1 or 0]
    # field_name and 1
    if isinstance(item_ast, ast.BoolOp):
        returns_boolean = True
        returns_domain = False

        values = []
        for ast_value in item_ast.values:
            value = _modifier_to_domain_ast_item(ast_value, should_contain_domain, need_parenthesis=True)
            if isinstance(value, ContextDependentDomainItem):
                vnames.update(value.contextual_values)
                if not value.returns_boolean:
                    returns_boolean = False
                if value.returns_domain:
                    returns_domain = True
            elif not isinstance(value, bool):
                returns_boolean = False
            values.append(repr(value))

        if returns_domain:
            raise ValueError("Use if/else condition instead of boolean operator to return domain.")

        if isinstance(item_ast.op, ast.Or):
            expr = ' or '.join(values)
        else:
            expr = ' and '.join(values)
        if need_parenthesis and (' ' in expr or len(values)>1 in expr):
            expr = f'({expr})'
        return ContextDependentDomainItem(expr, vnames, returns_boolean=returns_boolean)

    # [('a', '=', not context.get('abc', 'default')), ('a', '=', -1)]
    # not context.get('abc', 'default')
    if isinstance(item_ast, ast.UnaryOp):
        if isinstance(item_ast.operand, ast.Constant) and isinstance(item_ast.op, ast.USub) and isinstance(item_ast.operand.value, (int, float)):
            return -item_ast.operand.value

        leaf = _modifier_to_domain_ast_item(item_ast.operand, need_parenthesis=True)
        if isinstance(leaf, ContextDependentDomainItem):
            vnames.update(leaf.contextual_values)

        expr = f"not {leaf!r}"
        return ContextDependentDomainItem(expr, vnames, returns_boolean=True)

    # [('a', '=', int(context.get('abc', False))]
    # context.get('abc', False)
    if isinstance(item_ast, ast.Call):
        name = _modifier_to_domain_ast_item(item_ast.func, need_parenthesis=True)
        if isinstance(name, ContextDependentDomainItem) and name.value not in _BUILTINS:
            vnames.update(name.contextual_values)
        returns_boolean = str(name) == 'bool'

        values = []
        for arg in item_ast.args:
            value = _modifier_to_domain_ast_item(arg)
            if isinstance(value, ContextDependentDomainItem):
                vnames.update(value.contextual_values)
            values.append(repr(value))

        expr = f"{name!r}({', '.join(values)})"
        return ContextDependentDomainItem(expr, vnames, returns_boolean=returns_boolean)

    # [('a', '=', 1 if context.get('abc', 'default') == 'b' else 0)]
    # 1 if context.get('abc', 'default') == 'b' else 0
    if isinstance(item_ast, ast.IfExp):
        test = _modifier_to_domain_ast_item(item_ast.test)
        if isinstance(test, ContextDependentDomainItem):
            vnames.update(test.contextual_values)

        returns_boolean = True
        returns_domain = True

        body = _modifier_to_domain_ast_item(item_ast.body, should_contain_domain, need_parenthesis=True)
        if isinstance(body, ContextDependentDomainItem):
            vnames.update(body.contextual_values)
            if not body.returns_boolean:
                returns_boolean = False
            if not body.returns_domain:
                returns_domain = False
        else:
            returns_domain = False
            if not isinstance(body, bool):
                returns_boolean = False

        orelse = _modifier_to_domain_ast_item(item_ast.orelse, should_contain_domain, need_parenthesis=True)
        if isinstance(orelse, ContextDependentDomainItem):
            vnames.update(orelse.contextual_values)
            if not orelse.returns_boolean:
                returns_boolean = False
            if not orelse.returns_domain:
                returns_domain = False
        else:
            returns_domain = False
            if not isinstance(orelse, bool):
                returns_boolean = False

        if returns_domain:
            # [('id', '=', 42)] if parent.a else []
            not_test = ContextDependentDomainItem(f"not ({test})", vnames, returns_boolean=True)
            if not isinstance(test, ContextDependentDomainItem) or not test.returns_boolean:
                test = ContextDependentDomainItem(f"bool({test})", vnames, returns_boolean=True)
            # ['|', '&', bool(parent.a), ('id', '=', 42), not parent.a]
            expr = ['|', '&', test] + body.value + ['&', not_test] + orelse.value
        else:
            expr = f"{body!r} if {test} else {orelse!r}"

        return ContextDependentDomainItem(expr, vnames, returns_boolean=returns_boolean, returns_domain=returns_domain)

    if isinstance(item_ast, ast.Expr):
        return _modifier_to_domain_ast_item(item_ast.value)

    raise ValueError(f"Undefined item {item_ast!r}.")

def _modifier_to_domain_validation(domain):
    for leaf in domain:
        if leaf in DOMAIN_OPERATORS:
            continue
        if leaf in (TRUE_LEAF, FALSE_LEAF):
            continue
        try:
            left, operator, _right = leaf
        except ValueError:
            raise InvalidDomainError() from None
        except TypeError:
            if isinstance(leaf, ContextDependentDomainItem) and leaf.returns_boolean:
                continue
            raise InvalidDomainError() from None

def update_normalize_domain(domain):
    dom = []
    for leaf in domain:
        try:
            left, operator, right = leaf

            if operator not in VALID_TERM_OPERATORS:
                raise InvalidDomainError()

            # check domain leaf can be evaluated as per `domain.js`
            # https://github.com/odoo/odoo/blob/40b17cee0fb48691b80d98960ae6e2e54dabd1c6/addons/web/static/src/core/domain.js#L295-L302
            if left is None or left is False or left is True:
                leaf = FALSE_LEAF if operator in ('=', '==') else TRUE_LEAF
            elif isinstance(left, (int, float)):
                if operator in ('=', '=='):
                    leaf = TRUE_LEAF if left == right else FALSE_LEAF
                else:
                    leaf = TRUE_LEAF if left != right else FALSE_LEAF
            elif not isinstance(left, str):
                raise InvalidDomainError()
        except (ValueError, TypeError):
            if isinstance(leaf, ContextDependentDomainItem):
                pass
            elif leaf not in DOMAIN_OPERATORS:
                raise InvalidDomainError() from None
        dom.append(leaf)
    return normalize_domain(dom)

def modifier_to_domain(modifier):
    """
    Convert modifier values to domain. Generated domains can contain
    contextual elements (right part of domain leaves). The domain can be
    concatenated with others using the `AND` and `OR` methods.
    The representation of the domain can be evaluated with the corresponding
    context.

    :params modifier (bool|0|1|domain|str|ast)
    :return a normalized domain (list(tuple|"&"|"|"|"!"))
    """
    if isinstance(modifier, bool):
        return [TRUE_LEAF if modifier else FALSE_LEAF]
    if isinstance(modifier, int):
        return [TRUE_LEAF if modifier else FALSE_LEAF]
    if isinstance(modifier, (list, tuple)):
        return update_normalize_domain(modifier)
    if isinstance(modifier, ast.AST):
        try:
            return _modifier_to_domain_ast_domain(modifier)
        except Exception as e:
            raise ValueError(f'{e}: {modifier!r}') from None

    # modifier is a string
    modifier = modifier.strip()

    # most (~95%) elements are 1/True/0/False
    if modifier.lower() in ('0', 'false'):
        return [FALSE_LEAF]
    if modifier.lower() in ('1', 'true'):
        return [TRUE_LEAF]

    # [('a', '=', 'b')]
    try:
        domain = ast.literal_eval(modifier)
        return update_normalize_domain(domain)
    except SyntaxError:
        raise ValueError(f'Wrong domain python syntax: {modifier}')
    except ValueError:
        pass

    # [('a', '=', parent.b), ('a', '=', context.get('b'))]
    try:
        modifier_ast = ast.parse(f'({modifier})', mode='eval').body
        if isinstance(modifier_ast, ast.List):
            return _modifier_to_domain_ast_domain(modifier_ast)
        else:
            return _modifier_to_domain_ast_wrap_domain(modifier_ast)
    except Exception as e:
        raise ValueError(f'{e}: {modifier}')
