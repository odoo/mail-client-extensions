import collections
import itertools
import logging

from lxml import etree
from psycopg2.extras import Json

from odoo.modules.module import get_modules

from odoo.upgrade import util

fix_attrs = util.import_script("base/17.0.1.3/attr_domains2expr.py").fix_attrs
_logger = logging.getLogger(__name__)


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
    ordered_views = []
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
            if v.model == "board.board":
                # board views have a dedicated schema and don't need to be fixed.
                # Moreover, updating them using the ORM will lead to the lost of users' dashboards.
                continue
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
                    _logger.exception("Error in view %s", v.id)
            if active:
                cr.execute("UPDATE ir_ui_view SET active=true WHERE id=%s", [vid])
            md = v.model_data_id
            try:
                arch = etree.fromstring((v.arch_db or "").strip())
            except Exception:
                _logger.exception(
                    "Skipping adapt of attributes for view (id=%s, lang=%r) with invalid arch", v.id, lang
                )
                view_errors[v.id].append(lang)
                continue
            if not v.model:
                _logger.warning("Skipping adapt of attributes for model-less view (id=%s)", v.id)
            elif not md or md.module not in standard_modules or lang != "en_US":
                # fix only custom views, or translations
                if not fix_attrs(cr, v.model, arch, comb_arch):
                    _logger.warning("Some errors occurred while adapting arch of view (id=%s, lang=%s)", v.id, lang)
                    view_errors[v.id].append(lang)
                new_archs[v.id] = (active, arch)
            elif md.noupdate and util.module_installed(cr, md.module):
                # We cannot rely in the restore of the views fixer
                # it may fail if the view comes from a noupdate block
                try:
                    util.update_record_from_xml(cr, f"{md.module}.{md.name}")
                except ValueError:
                    # the xmlid may not exists.
                    # This is the case for the `worksheet` module (and its donwstream dependencies) that create dynamic models
                    # with views that have xmlids.
                    # Consider its a custom view.
                    if not fix_attrs(cr, v.model, arch, comb_arch):
                        _logger.warning(
                            "Some errors occurred while adapting arch of view %s.%s (id=%s, lang=%s)",
                            md.module,
                            md.name,
                            v.id,
                            lang,
                        )
                        view_errors[v.id].append(lang)
                    new_archs[v.id] = (active, arch)
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
               COALESCE(arch.value, '')
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
        try:
            parsed_arch = etree.fromstring(arch_db.strip())
        except Exception:
            _logger.exception("Skipping adapt of attributes for view (id=%s, lang=%r) with invalid arch", vid, lang)
            view_errors[vid].append(lang)
            continue
        if not check_arch(vid, parsed_arch, lang, error=False):
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
