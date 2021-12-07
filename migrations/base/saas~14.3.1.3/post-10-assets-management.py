# -*- coding: utf-8 -*-
import re

from lxml import etree
from psycopg2.extras import execute_values

from odoo.modules.module import get_modules

from odoo.addons.base.models.ir_asset import DIRECTIVES_WITH_TARGET, SCRIPT_EXTENSIONS, STYLE_EXTENSIONS

from odoo.upgrade import util

XPATH_POSITION_TO_DIRECTIVE = {
    "replace": "replace",
    "after": "after",
    "before": "before",
    "inside": "append",
}


def get_magic_query(cr, view_fields):
    """
     Returns the query that gets all ir.ui.view records
     corresponding to an asset definition (before-the-upgrade style).

     As previous-styled assets could contain a multitude of way to
     extend, inherit, call other asset definitions, this task is not trivial.

     This comment should help you to understand how the magic query works.

     Feel free to sit tight, grab a cup of coffee, a pencil and a notebook.

     --- Scheme ---

    (1)       (6)──C──►(11)──B──►(16)      (20)      (24)
     ▲         ▲                             ▲         ▲
     │         │                             │         │
     B         B                   ┌────C────┘         C
     │         │                   │                   │
    (2)──A──►[(7)]     (12)      (17)──C──►(21)      (25)
               ▲         ▲         ▲                   ▲
               │         │         │                   │
     ┌────A────┘         C         B                   B
     │                   │         │                   │
    (3)──A──►[(8)]─A─►[(13)]──B─►(18)──B──►(22)      (26)
     │         ▲                                       │
     │         │                                       C
     └────A────┘                                       │
                                                       ▼
    (4)──A──►[(9)]─A─►[(14)]──B─►(19)                (27)
     │         │                                       │
     C         C                                       B
     │         │                                       │
     ▼         ▼                                       ▼
    (5)      (10)──C──►(15)                (23)      (28)


     --- Legend ---
     x, y: view ids (x, y in VIds)
     x ──A──► y:  t-call-assets="y" in x
     x ──B──► y:  t-call="y" in x
     x ──C──► y:  y inherits from x
     (): graph node
     [()]: graph node called by a t-call-assets


     --- Algo ---
     Non-recursive term computes
     R_0 = { y in VIds | exists (x)──A──►(y) with x in VIds}

     Recursive term computes from R_i
     R_(i+1) = { y in VIds | exists (x)──B──►(y) or (x)──C──►(y) with x in R_i }

     When R_(i+1) is empty, stop.

     Solution is S = Union R_i

     --- Example ---
     R_0 = { 7, 8, 9, 13, 14 }
     R_1 = { 6, 10, 12, 18, 19 }
     R_2 = { 11, 15, 17, 22, }
     R_3 = { 16, 20, 21 }
     S = R_0 U ... U R_3 = { 6, 7, ..., 22 }
    """
    more_fields = ""
    if view_fields:
        fields_to_sql = list(map(lambda x: f'v."{x}"', view_fields))
        more_fields = ",".join([more_fields] + fields_to_sql)

    string_is_number_re = r"^[0-9]+$"

    return rf"""
WITH RECURSIVE assets_views AS (

  -- Initial term: all qweb views that are called with t-call-assets (A-arrow type on scheme)
  WITH sub AS (
        -- remove all &#13; coming from wrong migrations that replaced \r -> &#13;
    SELECT unnest(xpath('//@t-call-assets', regexp_replace(arch_db, E'&#13;\n', E'\n', 'g')::xml))::text AS tcalled
      FROM ir_ui_view
     WHERE type = 'qweb'
       AND arch_db ~ '\yt-call-assets\y'
  )
    SELECT v.id
      FROM sub
      JOIN ir_ui_view AS v
        ON v.key = sub.tcalled
        OR v.id = (CASE WHEN sub.tcalled ~ '{string_is_number_re}' THEN sub.tcalled::integer ELSE NULL END)
     WHERE v.type = 'qweb'
     UNION ALL
    SELECT d.res_id
      FROM sub
 LEFT JOIN ir_model_data AS d ON sub.tcalled = concat(d.module, '.', d.name)
     WHERE d.model = 'ir.ui.view'

  -- Recursive term
  UNION ALL
    (
        WITH arrows AS (
              (
                -- All t-calls in qweb views (B-arrow type on scheme)
                WITH sub AS (
                        -- remove all &#13; coming from wrong migrations that replaced \r -> &#13;
                    SELECT id, unnest(xpath('//@t-call', regexp_replace(arch_db, E'&#13;\n', E'\n', 'g')::xml))::text AS tcalled
                      FROM ir_ui_view
                     WHERE type = 'qweb'
                       AND arch_db ~ '\yt-call\y'
                )
                  SELECT sub.id AS source_id, v.id AS target_id
                    FROM sub
                    JOIN ir_ui_view AS v
                      ON v.key = sub.tcalled
                      OR v.id = (CASE WHEN sub.tcalled ~ '{string_is_number_re}' THEN sub.tcalled::integer ELSE NULL END)
                   WHERE v.type = 'qweb'
                   UNION ALL
                  SELECT sub.id AS source_id, d.res_id AS target_id
                    FROM sub
               LEFT JOIN ir_model_data AS d
                      ON sub.tcalled = concat(d.module, '.', d.name)
                   WHERE d.model = 'ir.ui.view'
             )
             UNION ALL
             (
               -- All inheritances in qweb views (C-arrow type on scheme)
                 SELECT v.inherit_id AS source_id, v.id AS target_id
                   FROM ir_ui_view AS v
                  WHERE type = 'qweb'
                    AND inherit_id IS NOT NULL
             )
        )
           SELECT ar.target_id
             FROM assets_views AS av
        LEFT JOIN arrows AS ar ON ar.source_id = av.id
            WHERE ar.target_id IS NOT NULL
    )

)
     SELECT DISTINCT ON (inherit_id, v.priority, v.name, v.id)
        d.module, d.name as xml_name, v.id, v.priority, v.name, COALESCE(v.inherit_id, 0) as inherit_id
        {more_fields}
     FROM assets_views AS av
     JOIN ir_ui_view AS v ON av.id = v.id
LEFT JOIN ir_model_data AS d ON v.id = d.res_id AND d.model = 'ir.ui.view' AND d.module != '__export__'
     WHERE v.type = 'qweb'
     ORDER BY inherit_id, v.priority, v.name, v.id;
"""


MIGR_CATEG = "Assets View to IrAsset"


class UnmigrableCase(Exception):
    pass


def migrate(cr, version):

    # TODO: remove this horror
    path_column = "path"
    if util.column_exists(cr, "ir_asset", "glob"):
        path_column = "glob"

    view_fields = ["arch_db", "mode", "active", "key"]
    # util.module_installed returns true for modules _about_ to be installed
    has_website = util.module_installed(cr, "website") and util.column_exists(cr, "ir_ui_view", "website_id")
    if has_website:
        view_fields.append("website_id")
        # Rename assets file
        cr.execute(
            r"""
            UPDATE ir_ui_view v
               SET arch_db = regexp_replace(arch_db,
                             '\yassets_(frontend|common)_minimal_js\y', 'assets_\1_minimal', 'g')
             WHERE type = 'qweb'
               AND website_id IS NOT NULL
               AND arch_db ~ '\yassets_(frontend|common)_minimal_js\y'
               AND NOT EXISTS (
                       SELECT 1
                         FROM ir_model_data
                        WHERE model = 'ir.ui.view'
                          AND res_id = v.id
                          AND noupdate IS TRUE
                       )
        """
        )

    query = get_magic_query(cr, view_fields)
    cr.execute(query)
    results = cr.dictfetchall()
    processed_results = process_views_conversion(cr, results, has_website=has_website, path_column=path_column)

    # remove views to remove
    for vid in processed_results["remove_view_ids"]:
        # Removal of all assets view is done in silent mode
        # We don't want a warning when a custom inheriting view
        # *happens* to be removed before its parents
        util.remove_view(cr, view_id=vid, silent=True)

    # deactivate unmigrable views
    unmigrable_ids = list(processed_results["keep_view_ids"])
    if unmigrable_ids:
        cr.execute(
            """
            DELETE FROM ir_model_data AS m
                  WHERE m.model = 'ir.ui.view'
                    AND m.res_id = ANY(%s);
        """,
            (unmigrable_ids,),
        )

        cr.execute(
            """
            UPDATE ir_ui_view
               SET active = false
             WHERE id = ANY(%s);
        """,
            (unmigrable_ids,),
        )

    if processed_results["to_create"]:
        # We always create the `website_id` column. It avoid having dynamic query constructs.
        # The column will be removed after INSERT if the `website` module is not installed.
        # (actually, if the module `website` isn't installed, the probability of having assets to create is low)
        util.create_column(cr, "ir_asset", "website_id", "integer")
        execute_values(
            cr._obj,
            f"INSERT INTO ir_asset(name, bundle, directive, {path_column}, target, active, sequence, website_id) VALUES %s",
            [
                (
                    a["name"],
                    a["bundle"],
                    a.get("directive", "append"),
                    a[path_column],
                    a.get("target"),
                    a["active"],
                    a["sequence"],
                    a.get("website_id"),
                )
                for a in processed_results["to_create"]
            ],
        )
        if not has_website:
            util.remove_column(cr, "ir_asset", "website_id")


def process_views_conversion(cr, results, has_website=False, path_column="path"):
    """
    Entry point to handle database results (all views considered as assets and their descendants)
    This function will make up irassets when possible,
    when not possible it will inactivate the view, and not create anything

    Its return should be used at different times in the migration process:
    - it should be executed as "pre", to grasp every asset that need to be migrated
    - relevant views are to be removed at the end of "pre"
    - objects (ir.assets) must be created in "end"

    This script has known pitfalls:
    - children nodes of t-call (that is, t-raw=0 stuff) are not handled
    - other <t> nodes are not handled
    - xpath position before./after when targetting a specific node is not well handled
    """

    # This should capture modules with a manifest in the addons_path
    # Given that an Odoo migration is done without any custom module in the path
    # We can assume this returns the list of modules that Odoo fully manages
    ODOO_SA_MODULES = get_modules()

    all_views = {view["id"]: view for view in results}
    assets_to_create = []
    do_not_delete_view_ids = set()
    unique_irasset = 0
    #
    # HELPERS
    #

    def get_base_view(view):
        inherit_id = view["inherit_id"]
        if not inherit_id or view["mode"] == "primary":
            return view
        return get_base_view(all_views[inherit_id])

    def get_view_key(view):
        module = view["module"]
        name = view["xml_name"]
        key = view["key"]
        if module and name:
            return ".".join([module, name])
        return key

    def get_ir_asset(view, bundle, values):
        nonlocal unique_irasset
        unique_irasset += 1
        defaults = {
            "name": get_view_key(view) + "--view_id:%s--%s" % (view["id"], unique_irasset),
            "bundle": bundle,
            "active": view["active"],
            "sequence": view["priority"],
        }
        website_id = has_website and view["website_id"] or None
        if website_id:
            defaults["website_id"] = website_id
        defaults.update(values)
        return defaults

    #  <xpath expr="//link[@href='/web/static/src/scss/dropdown_extra.scss']" position="replace" />
    regex_href = r"(href|src)\s*=\s*"
    regex_url_in_quotes = r'(?P<q>"|\')((/?\w+.?)+)(?P=q)'

    regex_xpath_target_url = re.compile(regex_href + regex_url_in_quotes)
    regex_last = re.compile(r"(link|script)\[(last)\(\)\]")

    def get_target_from_xpath(node, bundle_name):
        # https://github.com/SimonGenin/odoo-assets-scripts/blob/master/convert-cli.py
        # for ges xpath regex
        expr = node.get("expr")
        if expr:
            match = regex_xpath_target_url.search(expr)
            groups = match and match.groups()
            if groups:
                return groups[2]
            match = regex_last.search(expr)
            groups = match and match.groups()
            if groups:
                node_tag, position = groups
                if not position == "last":
                    return
                exts = None
                if node_tag == "script":
                    exts = SCRIPT_EXTENSIONS
                elif node_tag == "link":
                    exts = STYLE_EXTENSIONS
                last = None
                for asset in reversed(assets_to_create):
                    if asset["bundle"] == bundle_name:
                        ext = asset[path_column].rpartition(".")[2]
                        if not exts or ext in exts:
                            last = asset
                            break
                return last and last[path_column]

    # should map former view keys to jum's bundle names
    def get_bundle_name_from_key(view_key):
        return view_key

    # Checks if a asset key is only a view key
    # ie NOT a dynamic expression
    # <t t-call="{{company.external_report_layout_id.key}}" />
    asset_key_regex = re.compile(r"^(\w+.\w+)|(\d+)$")

    def get_asset_name_from_tcall(tcalled):
        if not tcalled:
            return
        match = asset_key_regex.match(tcalled)
        groups = match and match.groups() or (None, None)
        if groups[0]:
            return tcalled
        if groups[1]:
            view = all_views[int(groups[1])]
            return get_bundle_name_from_key(get_view_key(view))

    #
    # NODE HANDLERS
    #
    def handle_script_node(view, etreeNode):
        src = etreeNode.get("src")
        if not src:
            msg = """
                The view with id=%(view_id)s has the form:
                `<script>const code = 'someCode';</script>
                This is not supported. You should convert this script into an ir.attachement
                and make an ir.asset point to its url (/web/content/<id>/<filename>.js)
            """
            raise UnmigrableCase(msg)
        return dict([(path_column, src)])

    def handle_link_node(view, etreeNode):
        rel_attr = etreeNode.get("rel")
        if rel_attr == "stylesheet":
            msg = (
                """
                The view with id=%%(view_id)s contains:
                <link rel="%s" />
                This is not supported.
            """
                % rel_attr
            )
            raise UnmigrableCase(msg)
        return dict([(path_column, etreeNode.get("href"))])

    def handle_tcall(view, etreeNode, tcall):
        asset_key = get_asset_name_from_tcall(tcall)
        if not asset_key:
            msg = """
                The view with id=%(view_id)s has the form:
                `<t t-call="{some dynamic expression }" />`
                This is not supported.
            """
            raise UnmigrableCase(msg)

        if len(etreeNode):
            msg = """
                The view with id=%(view_id)s has the form:
                `<t t-call="some.view">
                    <someTag></someTag>
                </t>`
                This is not supported.
            """
            raise UnmigrableCase(msg)
        return dict([(path_column, asset_key)], directive="include")

    def handle_xpath(view, etreeNode, bundle_name):
        directive = XPATH_POSITION_TO_DIRECTIVE.get(etreeNode.get("position"))
        target = get_target_from_xpath(etreeNode, bundle_name)
        expr = etreeNode.get("expr")

        if (directive in DIRECTIVES_WITH_TARGET and not target) or (
            directive == "append" and not target and expr != "."
        ):
            msg = 'xpath target unsolvable for expr: "%s" in view_id: %%(view_id)s' % expr
            raise UnmigrableCase(msg)

        if len(etreeNode) == 0 and directive == "replace":
            return dict(directive="remove", target=target)

        assets = process_asset_node(etreeNode, bundle_name, view, directive, target)
        if directive in DIRECTIVES_WITH_TARGET:  # make a linked list from the first element on
            prev_glob = None
            for asset in assets:
                if prev_glob is not None:  # everything but the first element
                    asset["target"] = prev_glob
                    asset["directive"] = "after"
                prev_glob = asset[path_column]

        return assets

    def handle_generic_t_node(view, etreeNode):
        msg = """
            The view with id=%(view_id)s has the form:
            `<t t-[directive] />
            This is not supported because it implies dynamic asset generation.
        """
        raise UnmigrableCase(msg)

    def handle_style_node(view, etreeNode):
        msg = """
            The view with id=%(view_id)s has the form:
            `<style>.someclass { position:absolute; }</style>
            This is not supported. You should convert this stylesheet into an ir.attachement
            and make an ir.asset point to its url (/web/content/<id>/<filename>.css)
        """
        raise UnmigrableCase(msg)

    #
    # MAIN FUNCTION
    #
    def process_asset_node(arch, bundle_name, view, directive="append", target=None):
        result = []
        for node in arch:
            handler = None
            handler_args = [view, node]
            if node.tag == "script":
                handler = handle_script_node
            elif node.tag == "link":
                handler = handle_link_node
            elif node.tag == "t":
                tcall = node.get("t-call") or node.get("t-call-assets")
                if tcall:
                    handler = handle_tcall
                    handler_args.append(tcall)
                else:
                    handler = handle_generic_t_node
            elif node.tag == "xpath":
                handler = handle_xpath
                handler_args.append(bundle_name)
            elif node.tag == "style":
                handler = handle_style_node

            if handler:
                asset = handler(*handler_args)
                if asset and isinstance(asset, list):
                    result += asset
                elif asset:
                    to_create = get_ir_asset(view, bundle_name, dict(dict(target=target, directive=directive), **asset))
                    result.append(to_create)
            else:
                msg = """
                    The view with id=%(view_id)s has nodes that are ignored anyway by the asset generation algorithm.
                    e.g.: div, p ....
                """
                raise UnmigrableCase(msg)

        return result

    for view in results:
        module = view["module"]
        if module and module in ODOO_SA_MODULES:
            # do not care about stuff defined at GrandRosieres
            continue

        parent_view = get_base_view(view)
        bundle_name = get_bundle_name_from_key(get_view_key(parent_view))

        arch = etree.fromstring(view["arch_db"])
        if arch.tag == "data" and len(arch):
            arch = arch[0]
        if len(arch) == 0:
            continue

        try:
            ir_assets = process_asset_node(arch, bundle_name, view)
            if ir_assets:
                assets_to_create += ir_assets
        except UnmigrableCase as e:
            view_id = view["id"]
            msg = str(e) % {"view_id": view_id}
            util.add_to_migration_reports(msg, MIGR_CATEG)
            do_not_delete_view_ids.add(view_id)
            continue

    keep_view_chained = set()
    for vid in do_not_delete_view_ids:
        if vid in keep_view_chained:
            continue
        view_id = vid
        while view_id:
            keep_view_chained.add(view_id)
            view_id = all_views[view_id]["inherit_id"]

    return {
        "to_create": assets_to_create,
        "keep_view_ids": keep_view_chained,
        "remove_view_ids": (set(all_views.keys()) - keep_view_chained),
    }
