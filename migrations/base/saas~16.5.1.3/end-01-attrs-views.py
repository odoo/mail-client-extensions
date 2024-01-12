# -*- coding: utf-8 -*-
import ast
import collections
import itertools
import logging
import re
import uuid

from lxml import etree
from psycopg2.extras import Json

from odoo.modules.module import get_modules
from odoo.osv.expression import normalize_domain
from odoo.tools.safe_eval import safe_eval

from odoo.upgrade import util

_logger = logging.getLogger(__name__)

MODS = ["invisible", "readonly", "required", "column_invisible"]
DEFAULT_CONTEXT_REPLACE = {"active_id": "id"}
LIST_HEADER_CONTEXT_REPLACE = {"active_id": "context.get('active_id')"}


class InvalidDomainError(Exception):
    pass


class Ast2StrVisitor(ast._Unparser):
    """
    Extend standard unparser to allow specific names to be replaced.
    """

    def __init__(self, replace_names=None):
        self._replace_names = replace_names if replace_names else DEFAULT_CONTEXT_REPLACE
        super().__init__()

    def visit_Name(self, node):
        return self.write(self._replace_names.get(node.id, node.id))


def mod2bool_str(s):
    """
    Convert yes/no/true/false/on/off into True/False strings. Otherwise returns the input unchanged.
    The checked values would raise an error instead if used in a Python expression.
    Note that 0 and 1 are left unchanged since they have the same True/False meaning in Python.
    """
    ss = s.lower()
    if ss in "yes true on".split():
        return "True"
    if ss in "no false off".split():
        return "False"
    return s


def _clean_bool(s):
    """Minimal simplification of trivial boolean expressions"""
    return {
        "(1)": "1",
        "(0)": "0",
        "(True)": "True",
        "(False)": "False",
        "not (True)": "False",
        "not (False)": "True",
    }.get(s, s)


def target_elem_and_view_type(elem, comb_arch):
    """
    Find the target of an element. If there is no `comb_arch` or the element doesn't look like
    targeting anything (no position attributes) assume the input `elem` is the target and return it.
    Along with the target we also return the view type of the elem, plus the field path from the
    arch root.
    """

    def find_target(elem):
        # as in standard: github.com/odoo/odoo/blob/4fec6300/odoo/tools/template_inheritance.py#L73-L94
        if comb_arch is not None and elem.get("position"):
            if elem.tag == "xpath":
                it = iter(comb_arch.xpath(elem.get("expr")))
            elif elem.tag == "field":
                it = (x for x in comb_arch.iter("field") if x.get("name") == elem.get("name"))
            else:
                it = (
                    x
                    for x in comb_arch.iter("field")
                    if all(x.get(k) == elem.get(k) for k in elem.attrib if k != "position")
                )
            return next(it, elem)
        return elem

    field_path = []
    view_type = None
    telem = find_target(elem)
    pelem = telem.getparent()
    while pelem is not None:
        # the parent may be a targeting element (xpath or field tag with position attribute)
        # thus we need to ensure we got the parent's target
        pelem_target_position = pelem.get("position")
        pelem = find_target(pelem)
        if view_type is None and pelem.tag in (
            "kanban",
            "tree",
            "form",
            "calendar",
            "setting",
            "search",
            "templates",
            "groupby",
        ):
            view_type = pelem.tag
        if pelem.tag == "field" and (not pelem_target_position or pelem_target_position == "inside"):
            # if element is a normal <field/> or a targeting element with position="inside"
            field_path.append(pelem.get("name"))
        pelem = pelem.getparent()
    field_path.reverse()
    return telem, view_type, field_path


def is_simple_pred(expr):
    if expr in ("0", "1", "True", "False"):
        return True
    if re.match(r"""context\.get\((['"])\w+\1\)""", expr):
        return True
    return False


def fix_elem(cr, model, elem, comb_arch):
    success = True
    telem, inner_view_type, field_path = target_elem_and_view_type(elem, comb_arch)

    if elem.get("position") != "replace":
        telem = None  # do not take default attributes from the target element

    # Build the dict of attrs attributes:
    # 1. Take the values from the target element if any
    # 2. If current element has attrs, override the values.
    #    All keys in target not in current element are overriden as empty value.
    attrs = {}
    if telem is not None and "attrs" in telem.attrib:
        ast_attrs = ast_parse(telem.get("attrs"))
        if isinstance(ast_attrs, ast.Dict):
            attrs = {k.value: v for k, v in zip(ast_attrs.keys, ast_attrs.values)}
        else:
            _logger.log(
                util.NEARLYWARN if util.on_CI() else logging.ERROR,
                "Removing invalid `attrs` value %r from\n%s",
                telem.get("attrs"),
                etree.tostring(telem).decode(),
            )

    if "attrs" in elem.attrib:
        attrs_val = elem.get("attrs")
        ast_attrs = ast_parse(attrs_val)
        if isinstance(ast_attrs, ast.Dict):
            elem_attrs = {k.value: v for k, v in zip(ast_attrs.keys, ast_attrs.values)}
            attrs.update(elem_attrs)
            for k in attrs:
                if k not in elem_attrs:
                    attrs[k] = ast.Constant("")  # clear previous values
        else:
            _logger.log(
                util.NEARLYWARN if util.on_CI() else logging.ERROR,
                "Removing invalid `attrs` value %r from\n%s",
                attrs_val,
                etree.tostring(elem).decode(),
            )
        elem.attrib.pop("attrs")

    for mod in MODS:
        if mod not in elem.attrib and mod not in attrs:
            continue
        if inner_view_type == "kanban" and elem.tag == "field":
            # in kanban view, field outside <templates> should not have modifiers
            elem.attrib.pop(mod, None)
            continue
        # if mod is not in the blend of attrs from current element and target, then we don't
        # need to take the default value from target element since we can assume an override
        default_val = telem.get(mod, "") if telem is not None and mod in attrs else ""
        orig_mod = mod2bool_str(elem.get(mod, default_val).strip())
        try:
            attr_mod = (
                mod2bool_str(_clean_bool(convert_attrs_val(cr, model, field_path, attrs.get(mod))))
                if mod in attrs
                else ""
            )
        except InvalidDomainError as e:
            domain = e.args[0]
            _logger.error("Invalid domain `%s`, saved as data-upgrade-invalid-domain attribute", domain)  # noqa: TRY400
            hex_hash = uuid.uuid4().hex[:6]
            elem.attrib[f"data-upgrade-invalid-domain-{mod}-{hex_hash}"] = domain
            attr_mod = ""
            success = False
        # in list view we can switch the inline invisible into column_invisible
        # in case only the attrs invisible is present we can also use column_invisible
        if (
            mod == "invisible"
            and inner_view_type == "tree"
            and "column_invisible" not in elem.attrib
            and "column_invisible" not in attrs
        ):
            if is_simple_pred(orig_mod):
                elem.attrib.pop("invisible")
                elem.set("column_invisible", orig_mod)
                orig_mod = ""
            elif not orig_mod and is_simple_pred(attr_mod):
                elem.set("column_invisible", attr_mod)
                continue  # we know orig_mode is empty!

        # combine attributes
        if orig_mod and attr_mod:
            # short circuits for final_mod = (orig_mod or attr_mod)
            if orig_mod in ("True", "1") or attr_mod in ("True", "1"):
                final_mod = orig_mod
            elif orig_mod in ("False", "0"):
                final_mod = attr_mod
            elif attr_mod == ("False", "0"):
                final_mod = orig_mod
            else:
                final_mod = f"({orig_mod}) or ({attr_mod})"
        else:
            final_mod = orig_mod or attr_mod

        # set attribute if anything to set, or force empty if mod was present
        if final_mod or mod in attrs:
            elem.set(mod, final_mod)

    # special case to merge into invisible
    if "states" in elem.attrib:
        states = elem.attrib.pop("states")
        expr = "state not in [{}]".format(",".join(repr(x.strip()) for x in states.split(",")))
        invisible = elem.get("invisible")
        if invisible:
            elem.set("invisible", f"({invisible}) or ({expr})")
        else:
            elem.set("invisible", expr)

    for mod in MODS:
        attrs.pop(mod, None)
    # keys in attrs should be only one of MODS list, we inline here any "extra" value with a warning
    if attrs:
        extra = [key for key in attrs if key not in elem.attrib]
        _logger.log(
            util.NEARLYWARN if util.on_CI() else logging.WARN,
            "Extra values %s in `attrs` attribute will be inlined for element\n%s",
            extra,
            etree.tostring(elem).decode(),
        )
        extra_invalid = [key for key in attrs if key in elem.attrib]
        if extra_invalid:
            _logger.log(
                util.NEARLYWARN if util.on_CI() else logging.ERROR,
                "Attributes %s in `attrs` cannot be inlined because the inline attributes already exists",
                extra_invalid,
            )
        for key in extra:
            value = ast.unparse(attrs[key])
            _logger.info("Inlined %s=%r", key, value)
            elem.set(key, value)

    return success


def ast_parse(val):
    try:
        return ast.parse(val.strip(), mode="eval").body
    except SyntaxError:
        _logger.exception("Error for invalid code:\n%s", val)
        raise


def fix_attrs(cr, model, arch, comb_arch):
    success = True
    for elem in arch.xpath(
        "//attribute[@name='invisible' or @name='required' or @name='readonly' or @name='column_invisible']"
    ):
        if "value" in elem.attrib:
            elem.set("value", mod2bool_str(elem.get("value").strip()))
        elif elem.text:
            elem.text = mod2bool_str(elem.text.strip())

    # inline all attrs combined with already inline values
    for elem in arch.xpath("//*[@attrs or @states or @invisible or @required or @readonly or @column_invisible]"):
        success &= fix_elem(cr, model, elem, comb_arch)

    # remove context elements
    for elem in arch.xpath("//tree/header/*[contains(@context, 'active_id')]"):
        elem.set(
            "context",
            Ast2StrVisitor(LIST_HEADER_CONTEXT_REPLACE).visit(ast_parse(elem.get("context"))),
        )
    for elem in arch.xpath("//*[contains(@context, 'active_id')]"):
        elem.set("context", Ast2StrVisitor().visit(ast_parse(elem.get("context"))))

    # replace <attribute name=attrs> elements with individual <attribute name=mod>
    # use a fake field element to reuse the logic for Python expression conversion
    # <field name=... position=attributes>
    #   <attribute name=attrs>{invisible: xxx}</attribute>`
    #   <attribute name=invisible>yyy</attribute>`
    #   <attribute name=readonly value=zzz></attribute>`
    # </field>
    # becomes the fake element
    # <field name=... position=replace attrs={invisible: xxx} invisible=yyy readonly=zzz/>`
    for parent in arch.xpath("//*[@position='attributes']"):
        attrs_data = {}  # save the attributes from the children
        for elem in parent.findall("./attribute"):
            name = elem.get("name")
            if name in ["attrs", "states", *MODS]:
                attrs_data[name] = elem.get("value", elem.text or "").strip()
                parent.remove(elem)
            if name == "attrs" and not attrs_data["attrs"]:
                attrs_data["attrs"] = "{}"
        # keep track of extra keys in `attrs` if any
        extra_mods = [k.value for k in ast_parse(attrs_data.get("attrs", "{}")).keys if k.value not in MODS]
        fake_elem = etree.Element(parent.tag, {**parent.attrib, **attrs_data}, position="replace")
        success &= fix_elem(cr, model, fake_elem, comb_arch)
        for mod in MODS + extra_mods:
            if mod not in fake_elem.attrib:
                continue
            new_elem = etree.Element("attribute", name=mod)
            new_elem.text = fake_elem.get(mod)
            parent.append(new_elem)

    return success


def check_true_false(lv, ov, rv_ast):
    """
    Returns True/False if the leaf (lp, op, rp) is something that can be considered as a True/False leaf.
    Otherwise returns None.
    """
    ov = {"=": "==", "<>": "!="}.get(ov, ov)
    if ov not in ["==", "!="]:
        return None
    # Note: from JS implementation (None,=,xxx) is always False, same for (True/False,=,xxx)
    #       conversely if op is `!=` then this is considered True ¯\_(ツ)_/¯
    if isinstance(lv, bool) or lv is None:
        return ov == "!="
    if isinstance(lv, (int, float)) and isinstance(rv_ast, ast.Constant) and isinstance(rv_ast.value, (int, float)):
        return safe_eval(f"{lv} {ov} {rv_ast.value}")
    return None


def ast_term2domain_term(term):
    if isinstance(term, ast.Constant):
        return term.value
    if isinstance(term, (ast.Tuple, ast.List)):
        try:
            left, op, right = term.elts
        except Exception:
            util._logger.exception("Invalid domain!")
        else:
            return (left.value, op.value, right)
    raise SyntaxError("Domain terms must be either a domain operator either a three-elements tuple")


def convert_attrs_val(cr, model, field_path, val):
    """
    Convert an `attrs` value into a python formula. We need to use the AST representation because
    values representing domains could be:
    * an if, or boolean, expression returning alternative domains
    * a string constant with the domain
    * a list representing the domain directly
    """
    ast2str = Ast2StrVisitor().visit

    if isinstance(val, ast.IfExp):
        return "({} if {} else {})".format(
            convert_attrs_val(cr, model, field_path, val.body),
            ast2str(val.test),
            convert_attrs_val(cr, model, field_path, val.orelse),
        )
    if isinstance(val, ast.BoolOp):
        return "({})".format(
            (" and " if type(val.op) == ast.And else " or ").join(
                convert_attrs_val(cr, model, field_path, v) for v in val.values
            )
        )

    if isinstance(val, ast.Constant):  # {'readonly': '0'} or {'invisible': 'name'}
        val = str(val.value).strip()  # we process the right side as a string
        # a string should be interpreted as a field name unless it is a domain!!
        if val and val[0] == "[" and val[-1] == "]":
            val = ast_parse(val)
            return convert_attrs_val(cr, model, field_path, val)
        return mod2bool_str(val)

    if isinstance(val, ast.List):  # val is a domain
        orig_ast = val
        val = val.elts
        if not val:
            return "True"  # all records match the empty domain
        # make an ast domain look like a domain, to be able to use normalize_domain
        val = [ast_term2domain_term(term) for term in val]
        try:
            norm_domain = normalize_domain(val)
        except Exception:
            raise InvalidDomainError(ast.unparse(orig_ast)) from None
        # convert domain into python expression
        stack = []
        for item in reversed(norm_domain):
            if item == "!":
                top = stack.pop()
                stack.append(f"(not {top})")
            elif item in ("&", "|"):
                right = stack.pop()
                left = stack.pop()
                op = {"&": "and", "|": "or"}[item]
                stack.append(f"({left} {op} {right})")
            else:
                stack.append(convert_domain_leaf(cr, model, field_path, item))
        assert len(stack) == 1
        res = stack.pop()
        assert res[0] == "(" and res[-1] == ")", res
        return res[1:-1]

    return ast2str(val)


def target_field_type(cr, model, path):
    ttype = None
    for fname in path:
        cr.execute(
            """
            SELECT relation, ttype
              FROM ir_model_fields
             WHERE model = %s
               AND name = %s
             ORDER BY id
             LIMIT 1
            """,
            [model, fname],
        )
        model, ttype = cr.fetchone() if cr.rowcount else (None, None)
        if model is None:
            break
    return ttype


def convert_domain_leaf(cr, model, field_path, leaf):
    """
    Convert a domain leaf (tuple) into a python expression.
    It always return the expression surrounded by parenthesis such that it's safe to use it as a sub-expression.
    """
    left, op, right_ast = leaf
    tf = check_true_false(left, op, right_ast)
    if tf is not None:
        return f"({tf})"
    # string values in left must be interpreted as a field name
    # string values in right are constants, hence we must use repr
    # if isinstance(right, str):

    # see warnings from osv.expression.normalize_leaf
    # https://github.com/odoo/odoo/blob/7ff1dac42fe24d1070c569f99ae7a67fe66eda2b/odoo/osv/expression.py#L353-L358
    if op in ("in", "not in") and isinstance(right_ast, ast.Constant) and isinstance(right_ast.value, bool):
        op = "=" if op == "in" else "!="
    elif op in ("=", "!=") and isinstance(right_ast, (ast.List, ast.Tuple)):
        op = "in" if op == "=" else "not in"

    right = Ast2StrVisitor().visit(right_ast)
    if op == "=?":
        return f"({right} is False or {right} is None or ({left} == {right}))"
    if op in ("=", "=="):
        return f"({left} == {right})"
    if op in ("!=", "<>"):
        return f"({left} != {right})"
    if op in ("<", "<=", ">", ">="):
        return f"({left} {op} {right})"
    if op == "like":
        return f"({right} in ({left} or ''))"
    if op == "ilike":
        return f"({right}.lower() in ({left} or '').lower())"
    if op == "not like":
        return f"({right} not in ({left} or ''))"
    if op == "not ilike":
        return f"({right}.lower() not in ({left} or '').lower())"
    if op in ("in", "not in"):
        # this is a complex case:
        #  (user_ids, 'in', []) -> empty result
        #  (user_ids, 'in', [2]) -> the result cannot be evaluated as `users_ids == [2]` :/
        # from domain.js:
        # ```
        #  const val = Array.isArray(value) ? value : [value];
        #  const fieldVal = Array.isArray(fieldValue) ? fieldValue : [fieldValue];
        #  return fieldVal.some((fv) => val.includes(fv));
        # ```
        rv = f"{right}" if isinstance(right_ast, (ast.List, ast.Tuple)) else f"[{right}]"
        lv = str(left)
        ttype = target_field_type(cr, model, field_path + left.split("."))
        if isinstance(left, str) and ttype in ("one2many", "many2many"):  # array of ids
            res = f"set({lv}).intersection({rv})"  # odoo/odoo#139827, odoo/odoo#139451
            return f"(not {res})" if op == "not in" else f"({res})"
        else:
            # consider the left-hand side to be a single value
            # ex. ('team_id', 'in', [val1, val2, val3, ...]) => team_id in [val1, val2, val3, ...]
            return f"({lv} {op} {rv})"
    if op in ("=like", "=ilike") and isinstance(right_ast, ast.Constant) and isinstance(right_ast.value, str):
        # this cannot be handled in Python for all cases with the limited support of what
        # can be evaluated in an inline attribute expression, we try to deal with some cases
        # a pattern like 'aaa%bbb%ccc' is imposible to deal with
        pattern = right[1:-1]  # chop the quotes
        lower = ""
        if op == "=ilike":
            pattern = pattern.lower()
            lower = "lower()"
        if "%" not in pattern:
            return f"({left}{lower} == {pattern!r})"
        if pattern.count("%") == 1:  # pattern=aaa%bbbb
            start, end = pattern.split("%")
            return f"({left}{lower}.startswith({start!r}) and {left}{lower}.endswith({end!r}))"
        if pattern.count("%") == 2 and pattern[0] == "%" and pattern[-1] == "%":
            # pattern=%aaa%, same as `like` op with aaa
            pattern = pattern[1:-1]  # chop the %
            return f"({pattern!r} in {left}{lower})"
        # let it fail otherwise
    raise ValueError("Cannot convert leaf to Python (%s, %s, %s)", left, op, right)


def get_ordered_views(cr):
    # The main algorithm in which views are applied is:
    # 1. Construct the path to root from requested view going up via inherith_id.
    # 2. Extend the path recursively with all extension views that have the same model
    #    as its parent.
    # 3. Apply extension views from the top in DFS fashion, appying always all extension
    #    views descendants _before_ any direct primary view child.
    #         R---+       - X* means X is primary view,
    #        / \   \      - the order we show children already follows
    #       B*  E   I*      the (mode,id) order for siblings
    #      / \  | \       Rendering A:
    #     A*  C H* F      1. Its path to root is [A, B, R],
    #         |   / \     2. Add extensions [C, D, E, F, G, J], note I and H are out,
    #         D  G   J    3. The apply order is then [R, E, F, G, J, B, C, D, A]
    vinfo = collections.namedtuple("vinfo", "mode priority id inherit_id active")
    cr.execute(
        """
        SELECT mode,
               priority,
               id,
               inherit_id,
               active
          FROM ir_ui_view
         WHERE type != 'qweb'
      ORDER BY id
        """
    )
    data = {r.id: r for r in itertools.starmap(vinfo, cr.fetchall())}
    children = collections.defaultdict(list)
    for v in data.values():
        children[v.inherit_id].append(v)
    ordered_views = [(v.id, v.active) for v in children[None]]  # first root views
    for root in children[None]:
        dq = collections.deque([root])
        while dq:
            v = dq.popleft()
            ordered_views.append((v.id, v.active))
            for c in sorted(children[v.id], reverse=True):
                if c.mode == "extension":
                    dq.appendleft(c)
                else:
                    dq.append(c)
    return ordered_views


def check_arch(vid, arch, lang, error=True):
    level = util.NEARLYWARN if util.on_CI() else logging.ERROR if error else logging.WARN
    good = True
    for elem in arch.xpath("//attribute[@name='states' or @name='attrs'] | //*[@attrs or @states]"):
        good = False
        _logger.log(
            level, "Incomplete conversion for view(id=%s, lang=%s) at\n%s", vid, lang, etree.tostring(elem).decode()
        )
    return good


def migrate(cr, version):
    # The order we fix views is important. We want to fix a view before any other view
    # that modifies it. Since the order in which views are applied in Odoo is "complex"
    # we need to pre compute it.
    info = get_ordered_views(cr)
    # We disable all views to ensure they do not contribute to the combined arch
    # they will be re-enabled according to the order computed before
    for ids in util.chunks((vid for (vid, _) in info), 1000, tuple):
        cr.execute("UPDATE ir_ui_view SET active = False WHERE id IN %s", [ids])
    standard_modules = set(get_modules())

    view_errors = collections.defaultdict(list)  # view.id -> langs

    def fix_archs(info, lang="en_US"):
        IrUiView = util.env(cr)["ir.ui.view"].with_context(load_all_views=True, lang=lang)
        new_archs = {}
        for vid, active in info:
            IrUiView.invalidate_model()
            v = IrUiView.browse(vid)
            comb_arch = None
            # We do not get combined arch for inactive views, they can cause many issues
            # TODO: skip also combined arch if parent is inactive?
            if active and v.inherit_id:
                try:
                    # Since during the upgrade _check_xml is defused, this should return
                    # the actual combined XML even if odoo 17.0 won't "normally" accept them.
                    # We need to combine the original archs to ensure we set the right attrs.
                    # The combined arch don't take into account current view since it's disabled.
                    comb_arch = v.inherit_id._get_combined_arch()
                except Exception:
                    util._logger.exception("Error in view %s", v.id)
            v.active = active
            v.flush_recordset()
            md = v.model_data_id
            arch = etree.fromstring(v.arch_db)
            if not v.model:
                _logger.warning("Skipping adapt of attributes for model-less view (id=%s)", v.id)
            elif not md or md.module not in standard_modules or lang != "en_US":
                # fix only custom views, or translations
                if not fix_attrs(cr, v.model, arch, comb_arch):
                    view_errors[v.id].append(lang)
                new_archs[v.id] = (active, arch)
            else:
                # We cannot rely in the restore of the views fixer
                # it may fail if the view comes from a noupdate block
                util.update_record_from_xml(cr, f"{md.module}.{md.name}")
        return new_archs

    # Now we update all archs at once, this updates also translations
    new_archs = fix_archs(info)
    for vid, (active, new_arch) in new_archs.items():
        with util.edit_view(cr, view_id=vid, active=active) as arch:
            arch.clear()
            arch.attrib.update(new_arch.attrib)
            arch.text = new_arch.text
            arch.extend(new_arch)
            check_arch(vid, arch, "en_US", error=True)

    # At this point all bases archs should be fine: i.e. lang en_US archs should be fine
    # edit_view could leave non-updated attributes in the edited archs for non en_US
    # langs because translations are imperfect, for <span> elements for example
    cr.execute(
        """
        SELECT arch.id,
               arch.lang,
               arch.value
          FROM ir_ui_view v
          JOIN LATERAL (
               SELECT v.id,
                      arch.key,
                      arch.value
                 FROM jsonb_each_text(arch_db) arch
               ) AS arch(id, lang, value)
            ON v.id = arch.id
         WHERE arch.lang != 'en_US'
           AND v.type != 'qweb'
         ORDER BY v.id
        """
    )
    to_process = collections.defaultdict(set)
    for vid, lang, arch_db in cr.fetchall():
        if not check_arch(vid, etree.fromstring(arch_db), lang, error=False):
            to_process[lang].add(vid)
    for lang, process_ids in to_process.items():
        # we need the order per lang!
        new_archs = fix_archs([x for x in info if x[0] in process_ids], lang=lang)
        data = {}
        for vid, (_, new_arch) in new_archs.items():
            check_arch(vid, new_arch, lang, error=True)
            data[vid] = etree.tostring(new_arch).decode()
        if data:  # maybe the failing views were standard which we do not fix, hence data could be empty
            cr.execute(
                """
                UPDATE ir_ui_view
                   SET arch_db = jsonb_set(arch_db, %s, (%s::jsonb->id::text), false)
                 WHERE id IN %s
                """,
                [f"{{{lang}}}", Json(data), tuple(data)],
            )

    if not view_errors:
        return
    # report issues
    cr.execute(
        """
        SELECT v.id,
               v.name,
               d.module || '.' || d.name
          FROM ir_ui_view v
     LEFT JOIN ir_model_data d
            ON d.res_id = v.id
           AND d.model = 'ir.ui.view'
         WHERE v.id IN %s
        """,
        [tuple(view_errors)],
    )
    msg = """
    <details>
        <summary>
            The following views had invalid domains in their attributes. The invalid domains were kept as
            <code>upgrade-data-invalid-domain-&lt;...&gt;</code> attributes. Some translations may be also affected.
        </summary>
    <ul>{}</ul>
    </details>
    """.format(
        "\n".join(
            "<li>{} for language(s): {}</li>".format(
                util.get_anchor_link_to_record("ir.ui.view", vid, (xmlid or name) + f"(id={vid})"),
                ",".join(view_errors[vid]),
            )
            for vid, name, xmlid in cr.fetchall()
        )
    )

    util.add_to_migration_reports(msg, category="Views", format="html")
