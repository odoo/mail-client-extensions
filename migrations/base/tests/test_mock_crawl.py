import contextlib
import inspect
import logging
import math
import re
from ast import literal_eval
from traceback import format_exception
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import fields
from odoo.exceptions import AccessError, RedirectWarning, UserError
from odoo.tools import OrderedSet, mute_logger
from odoo.tools.safe_eval import safe_eval
from odoo.tools.sql import table_kind

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import IntegrityCase

try:
    from odoo.fields import Domain

    AND, OR = Domain.AND, Domain.OR
except ImportError:
    from odoo.osv.expression import AND, OR

try:
    # v14+ forbids raw modules in eval context, use the wrapped ones instead
    from odoo.tools.safe_eval import datetime, time

    to_patch = "odoo.tools.safe_eval.datetime.datetime"
except ImportError:
    try:
        # older versions may have wrapped modules too
        from odoo.tools.misc import datetime, time

        to_patch = "odoo.tools.misc.datetime.datetime"
    except ImportError:
        import datetime
        import time

        to_patch = "datetime.datetime"

try:
    from odoo.tools.sql import TableKind

    regular_types = ("r", TableKind.Regular)
    view_table_types = ("v", "m", TableKind.View, TableKind.Materialized)
except ImportError:
    regular_types = ("r",)
    view_table_types = ("v", "m")

NS = "odoo.addons.base.maintenance.migrations.base.tests"
_logger = logging.getLogger(NS + __name__)


def get_id(rec, name):
    if name == "id":
        return rec._ids[0] if rec._ids else False
    if name == "__last_update":
        return False
    if name == "display_name":
        return "Unknown record" + " (id={})".format(rec._ids[0]) if rec._ids else ""
    return getattr(rec, name)


if util.version_gte("saas~16.4"):

    def read_display_name(recordset):
        recordset.mapped("display_name")

else:

    def read_display_name(recordset):
        recordset.name_get()


class TestCrawler(IntegrityCase):
    view_tracebacks = {}

    def setUp(self):
        super().setUp()
        if hasattr(self.env["ir.actions.report"], "_render"):
            if len(inspect.signature(self.env["ir.actions.report"]._render).parameters) == 3:
                self.render_method = self.env["ir.actions.report"]._render
            else:

                def render(name, res_id, data):
                    report = self.env["ir.actions.report"].search([("report_name", "=", name)])
                    self.assertTrue(report)
                    return report._render(res_id, data)

                self.render_method = render
        else:

            def render(name, res_id, data):
                report = self.env["ir.actions.report"].search([("report_name", "=", name)])
                self.assertTrue(report)
                return report.render(res_id, data)

            self.render_method = render

        self.skip_menus = []
        cr = self.env.cr
        if util.on_CI() and util.version_gte("saas~16.3") and util.module_installed(cr, "l10n_fr_hr_holidays"):
            self.skip_menus.extend(
                [
                    "hr_holidays.hr_leave_menu_new_request",
                    "hr_holidays.hr_leave_menu_my",
                    "hr_holidays.menu_open_department_leave_approve",
                    "hr_holidays.hr_holidays_status_menu_configuration",
                ]
            )
        if util.module_installed(cr, "l10n_fr_pos_cert"):
            self.skip_menus.append("l10n_fr_pos_cert.menu_check_move_integrity_reporting")

        if util.version_gte("18.0"):
            # These two menus commit the cursor because they reuse code meant for a cron
            # TODO: if the menus ever get fixed remove this.
            if util.module_installed(cr, "stock"):
                self.skip_menus.append("stock.menu_procurement_compute")
            if util.module_installed(cr, "mrp"):
                self.skip_menus.append("mrp.menu_procurement_compute_mrp")

    def check(self, value):
        """
        @Extend
        Check the diff of actions/views not working after and before.
        @param {list(tuple(xmlid, id, name, action_id))} value: the list of menus not working before upgrade.
            xmlid: xmlid of the menu
            id: id of the menu
            name: complete name of the menu (including parents)
            action_id: the id of the menu
        The items in the tuple are compared using an OR operator, not an AND.
        Meaning, if at least the menu xmlid, or id, or name, or action_id
        can be found in the faulty menus before upgrade,
        then we consider the faulty menu after upgrade was already failing before upgrade.
        This is done because:
         - Sometimes the xmlid of a menu changes (of name, or module) but if the rename is handled in an upgrade script
         then the id doesn't change.
         - Sometimes, the xmlid and id changes, but the complete name name doesn't. We can match on that.
         - Sometimes, the xmlid, id, and complete name change, but the action id remained the same.
        """
        test_start = datetime.datetime.fromtimestamp(value[1])
        before = [tuple(v) for v in value[0]]
        after, _ = self.invariant()

        diff = []
        for a in after:
            for i in range(len(a)):
                if a[i] in [b[i] for b in before]:
                    break
            else:
                menu_create = self.env["ir.ui.menu"].browse(a[1]).sudo().create_date
                if menu_create >= test_start:
                    _logger.warning("A new menu is failing: %s", a)
                else:
                    diff.append(a)

        _logger.info("Before: %s", before)
        _logger.info("After: %s", after)
        _logger.info("Diff: %s", diff)

        tracebacks_info = "\n\n".join("{}:\n {}\n".format(x, self.view_tracebacks[x]) for x in diff)
        msg = "At least one menu or view working before upgrade is not working after upgrade.\n\n{}".format(
            tracebacks_info
        )
        self.assertFalse(diff, msg)

    @patch("odoo.addons.base.models.ir_model.Unknown.__getattr__", get_id, create=True)
    def invariant(self):
        now = time.time()

        self.action_type_fields = {
            action_type: list(self.env.registry[action_type]._fields)
            for action_type in [*list(self.env.registry["ir.actions.actions"]._inherit_children), "ir.actions.actions"]
        }

        # Try to use an admin to crawl the menus, if not fallback on using an employee.
        field_group_ids = "all_group_ids" if util.version_gte("saas~18.2") else "groups_id"
        for group in ["base.group_system", "base.group_erp_manager", "base.group_user"]:
            user = (
                self.env["res.users"]
                .sudo()
                .search([(field_group_ids, "in", self.env.ref(group).id)], order="id", limit=1)
            )
            if user:
                self.env = self.env(user=user)
                break

        failing = set()

        # 1. Set base models and fields coming from custom modules to manual models and fields
        #    so more models and fields are loaded in the registry.
        #    Even if the behavior of the fields might not be entirely correct,
        #    this will help to have less errors when building views,
        #    making read, search and read_group, ..., so it validates more menus.
        #    Besides, this will be reverted at the end of the unit test as no commit occurs in tests.
        #    This is mainly for on-premise and odoo.sh databases, as saas databases do not have any custom modules.
        # 2. Mute the exceptions due to the missing filestore
        with util.custom_module_field_as_manual(self.env), mute_logger("odoo.addons.base.models.ir_attachment"):
            # 3. Do not validate manual selection fields
            #    Do not validate reference fields adding new possible custom model to their values
            origin_reference_convert_to_cache = fields.Reference.convert_to_cache
            with patch("odoo.fields.Selection.convert_to_cache", lambda s, v, r, validate=True: v or False), patch(
                "odoo.fields.Reference.convert_to_cache",
                lambda s, v, r, validate=True: origin_reference_convert_to_cache(s, v, r, validate=False),
            ):
                if hasattr(self.env, "companies"):
                    company = self.env.user.company_id
                    while company.parent_id:
                        company = company.parent_id
                    children = company.child_ids
                    while not (children.child_ids <= children):
                        children |= children.child_ids
                    company_ids = list(set(self.env.user.company_ids.ids).intersection(company.ids + children.ids))
                    self.env = self.env(context=dict(self.env.context, allowed_company_ids=company_ids))
                self.env.cr.execute("SAVEPOINT test_mock_crawl")
                _logger.info("Mocking menus with user %s(#%s) ", self.env.user.login, self.env.user.id)
                all_menus = self.env["ir.ui.menu"].load_menus(debug=False)

                if util.version_gte("saas~14.5"):
                    root_menu = all_menus["root"]

                    def get_menu(menu_id):
                        return all_menus[menu_id]

                else:
                    root_menu = all_menus

                    def get_menu(menu):
                        return menu

                for menu in root_menu["children"]:
                    failing.update(self.crawl_menu(get_menu(menu), get_menu))

        return [list(failing), now]

    def _safe_eval(self, value, extra_ctx=None):
        eval_context = {
            "uid": self.env.user.id,
            "tz": self.env.user.tz,
            "lang": self.env.user.lang,
            "datetime": datetime,
            "context_today": lambda: fields.Date.context_today(self.env.user),
            "time": time,
            "relativedelta": relativedelta,
            "current_date": time.strftime("%Y-%m-%d"),
            "allowed_company_ids": [self.env.user.company_id.id],
            "context": {},
        }
        if util.version_gte("13.0"):
            eval_context["current_company_id"] = self.env.company.id
        eval_context.update(extra_ctx or {})
        # JS Framework added a non standard `to_utc` method on datetime
        # e.g. `datetime.datetime.combine(context_today(), datetime.time(0,0,0)).to_utc()`
        # Can't directly patch `to_utc` to existing `datetime.datetime`:
        # `TypeError: can't set attributes of built-in/extension type 'datetime.datetime'`
        # https://stackoverflow.com/a/4482067
        with patch(to_patch, datetime_extended):
            return safe_eval(value, eval_context)

    def crawl_menu(self, menu, get_menu, parent=None):
        menu_name = "{} > {}".format(parent, menu["name"]) if parent else menu["name"]
        _logger.info("Mocking menu %s", menu_name)
        failing = set()
        if menu["xmlid"] in self.skip_menus:
            _logger.info("Skip known failing menu %s", menu["xmlid"])
        elif menu.get("action") or menu.get("action_id"):
            action_id = int(menu["action"].split(",")[1]) if menu.get("action") else menu["action_id"]
            action = self.env["ir.actions.actions"].sudo().browse(action_id)
            try:
                action_typed = self.env[action.type].sudo().browse(action_id)
                [action_vals] = action_typed.read(self.action_type_fields[action.type])
                self.mock_action(action_vals)
            except Exception as e:
                self.env.cr.execute("ROLLBACK TO SAVEPOINT test_mock_crawl")  # In case the cursor is broken
                failing_menu = (menu["xmlid"], menu["id"], menu_name, action_id)
                self.view_tracebacks[failing_menu] = " ".join(format_exception(type(e), e, e.__traceback__))
                _logger.exception("Adding menu %s to the failing menus", failing_menu)
                failing.add(failing_menu)
        for child in menu.get("children"):
            failing.update(self.crawl_menu(get_menu(child), get_menu, menu_name))
        return failing

    def mock_action(self, action):
        if action["type"] == "ir.actions.act_window":
            return self.mock_act_window(action)
        elif action["type"] == "ir.actions.server":
            try:
                action = self.env[action["type"]].browse(action["id"]).run()
            except UserError:
                # Ignore, in the web client, it would only display a warning dialog
                # e.g. in 13.0, Accounting > Configuration > Payments > Add a Bank Account
                # triggering `setting_init_bank_account_action` of `account_online_sync/models/company.py`
                # raising a UserError to tell the user he must create a bank journal if he has not one yet.
                return None
            except RedirectWarning as redirect:
                # Action can redirect to another with a message.
                # e.g. in 14.0, the method `setting_init_bank_account_action` of `account_online_sync/models/company.py`
                # now raise a `RedirectWarning`.
                action_id = redirect.args[1]
                action_type = self.env["ir.actions.actions"].browse(action_id).type
                [action] = self.env[action_type].browse(action_id).read(self.action_type_fields[action_type])
            return self.mock_action(action)
        elif action["type"] in ("ir.actions.client", "ir.actions.act_url"):
            return None
        elif action["type"] == "ir.actions.report":
            result = self.render_method(action["report_name"], [], data=None)
            if result:
                data, report_format = result
                self.assertTrue(data)
            return None
        else:
            _logger.error("Action %r is not implemented", action["type"])
            return None

    def mock_act_window(self, action):
        context = action.get("context") or {}
        if isinstance(context, str):
            context = self._safe_eval(context) if context else {}
        env = self.env(context=dict(self.env.context, **context))
        model = env[action["res_model"]]
        if not action.get("views"):
            # See `generate_views` in `addons/web/controllers/main.py`
            # Use case: xmlid `act_hr_employee_holiday_request`
            view_modes = action["view_mode"].split(",")
            action["views"] = [(False, mode) for mode in view_modes]
            view_id = action.get("view_id")
            if view_id:
                action["views"][0] = (view_id[0] if isinstance(view_id, (list, tuple)) else view_id, view_modes[0])

        if not (action.get("target") == "new" and action["views"] and action["views"][0][1] == "form"):
            # Ask for the search view, except if the menu simply loads a form dialog
            # e.g. a menu opening a dialog with a form the user have to set to display a report with given parameters
            # e.g. Point of Sale / Reporting / Sales Details
            # This mimics the behavior of the web client:
            # 10.0: https://github.com/odoo/odoo/blob/28c3f51c4878fbcd79b2e819948465fcf2160ebc/addons/web/static/src/js/action_manager.js#L666
            # 16.0: https://github.com/odoo/odoo/blob/f87b81ca9477cb499fd7cd2f402b64e3b40fddcf/addons/web/static/src/webclient/actions/action_service.js#L230-L234
            search_view_id = action.get("search_view_id")
            if isinstance(search_view_id, (list, tuple)):
                search_view_id = search_view_id[0]
            action["views"].append((search_view_id, "search"))

        Action = env.registry["ir.actions.actions"]
        with contextlib.ExitStack() as stack:
            origin_read = Action.read
            action_fields = self.action_type_fields["ir.actions.actions"]
            if not util.version_gte("15.0"):
                stack.enter_context(
                    patch.object(
                        # To specify the list of fields to read on actions,
                        # because `get_bindings` calls read without passing the list fields,
                        # and it therefore reads alls the fields, and some custom fields might be broken.
                        Action,
                        "read",
                        lambda self, *args, **kwargs: origin_read(self, fields=action_fields),
                    )
                )
            if hasattr(Action, "flush"):
                origin_flush = getattr(Action, "flush", None)
                stack.enter_context(
                    patch.object(
                        # To avoid the call to self.flush() in ir.actions that will try to recompute
                        # all fields, some fields may have a failed compute from previous actions
                        Action,
                        "flush",
                        lambda self, *args, **kwargs: (self or args or kwargs) and origin_flush(self, *args, **kwargs),
                    )
                )
            get_views = getattr(model, "get_views", None) or model.load_views
            views = get_views(
                action["views"], options={"action_id": action.get("id"), "toolbar": True, "load_filters": True}
            )
            views = views.get("fields_views") or views.get("views")
        env["ir.filters"].get_filters(model._name, action_id=action.get("id"))

        domain, group_by = [], []
        if views.get("search"):
            view = etree.fromstring(views["search"]["arch"])
            domain, group_by = self.mock_view_search(model, view, action.get("domain"))

        kind_of_table = table_kind(self.env.cr, model._table)
        is_view = kind_of_table in view_table_types
        is_query = kind_of_table is None
        view_columns = set(util.get_columns(env.cr, model._table, ignore=[])) if is_view else set()
        stored_fields = (
            {name for name, field in model._fields.items() if field.store and not field.type.endswith("2many")}
            if is_view
            else set()
        )

        if not kind_of_table and not getattr(model, "_table_query", None):
            # Dashboard module: a menu / action without table or view.
            return

        stored_custom_fields = [
            field.name
            for field in model._fields.values()
            if field.manual and not field.name.startswith("x_") and field.store and not field.type.endswith("2many")
        ]

        if is_query and stored_custom_fields:
            _logger.warning(
                "Mocking of model %s skipped because it is query-based model and still has some "
                "stored custom fields (%r). Perhaps the model switched to be query-based during the upgrade.",
                model._name,
                stored_custom_fields,
            )
            return

        if is_view and not view_columns.issuperset(stored_fields):
            # Report SQL views with unkown columns.
            missing_columns = stored_fields - view_columns
            _logger.warning(
                "Mocking of model %s skipped because it is based on an SQL view without all stored fields (missing %r). "
                "This is only possible with a custom module or a very technical manual intervention.",
                model._name,
                missing_columns,
            )
            return

        if any(
            # we need to check for None since the view is gone on test_check
            table_kind(self.env.cr, self.env[field.comodel_name]._table) not in regular_types
            for field in model._fields.values()
            if field.manual and field.comodel_name
        ):
            _logger.warning(
                "Mocking of model %s skipped because it has a manual related field with a SQL view as comodel.",
                model._name,
            )
            return

        for view_type, data in views.items():
            if view_type == "search":
                # Ignore, the searh view is already mocked before.
                # Otherwise we get an error in the number of args below when we call it.
                continue
            mock_method = getattr(self, "mock_view_{}".format(view_type), None)
            if mock_method:
                _logger.info("Mocking %s %s view ", model._name, view_type)
                view = etree.fromstring(data["arch"])
                fields_list = list(
                    OrderedSet(el.get("name") for el in view.xpath("//field[not(ancestor::field|ancestor::groupby)]"))
                )

                mock_method(model, view, fields_list, domain, group_by)

    def mock_view_activity(self, model, view, fields_list, domain, group_by):
        if util.column_exists(self.env.cr, "mail_activity", "active"):
            domain = AND([domain, [("activity_ids.active", "in", [True, False])]])
        else:
            domain = AND([domain, [("activity_ids", "!=", False)]])
        self.env["mail.activity"].get_activity_data(model._name, domain)

    def mock_view_calendar(self, model, view, fields_list, domain, group_by):
        pass

    def mock_view_cohort(self, model, view, fields_list, domain, group_by):
        pass

    def mock_view_dashboard(self, model, view, fields_list, domain, group_by):
        pass

    def mock_view_form(self, model, view, fields_list, domain, group_by):
        relation_fields_to_read = OrderedSet(
            node.get("name")
            for node in view.xpath("//field[not(ancestor::field|ancestor::groupby)]")
            if node.get("widget", "").startswith("many2many_")
        )
        records = model.search(domain, limit=3)
        _logger.info("view_form, %s, %s", records, domain)
        for i in range(len(records)):
            # `records[i]` is to exactly mimic the web client.
            # `for record in records` would prefetch the fields of all the records
            # and not one by one as a form view would do.
            record = records[i]
            if util.version_gte("18.0"):
                try:
                    [data] = record.read(fields_list)
                except AccessError as e:
                    ctx = dict(self.env.context)
                    allowed_company_ids = list(ctx.get("allowed_company_ids", []))
                    suggested_id = getattr(e, "context", {}).get("suggested_company", {}).get("id")
                    if suggested_id and suggested_id not in allowed_company_ids:
                        allowed_company_ids.append(suggested_id)
                        [data] = record.with_context(allowed_company_ids=allowed_company_ids).read(fields_list)
                    else:
                        raise
            else:
                [data] = record.read(fields_list)

            for fname in relation_fields_to_read:
                read_display_name(model.env[model._fields[fname].comodel_name].browse(data[fname]).sudo())

            processed_data = {}
            for fname, value in data.items():
                if fname in model._fields and model._fields[fname].type == "many2one" and value:
                    value = value[0]  # noqa: PLW2901
                processed_data[fname] = value

            for node in view.xpath("//field[not(ancestor::field|ancestor::groupby)][@widget='statusbar']"):
                fname = node.get("name")
                field = model._fields[fname]
                if field.comodel_name:
                    domain = []
                    if node.get("domain"):
                        domain = [("id", "=", processed_data[fname])] if processed_data[fname] else []
                        domain = OR([domain, self._safe_eval(node.get("domain"), extra_ctx=dict(**processed_data))])

                    fields_to_read = ["id"]
                    if node.get("options"):
                        opts = re.sub(r"\b(true|false)\b", lambda x: x.group().title(), node.get("options"))
                        options = literal_eval(opts)
                        if options.get("fold_field"):
                            fields_to_read.append(options["fold_field"])

                    values = self.env[field.comodel_name].search_read(domain, fields_to_read)
                    read_display_name(self.env[field.comodel_name].browse([value["id"] for value in values]))

            for node in view.xpath("//field[@widget='selection']"):
                sel_model = model
                if node.get("name") not in model._fields:
                    fields_path = []
                    parent = node.getparent()
                    while parent is not None:
                        if parent.tag == "field":
                            fields_path.append(parent.get("name"))
                        parent = parent.getparent()
                    while fields_path:
                        fname = fields_path.pop()
                        sel_model = self.env[sel_model._fields[fname].comodel_name]
                fname = node.get("name")
                field = sel_model._fields[fname]
                if field.comodel_name:
                    domain = []
                    if node.get("domain"):
                        domain = self._safe_eval(node.get("domain"), extra_ctx=dict(**processed_data))
                    domain_arg = {"domain" if util.version_gte("saas~18.3") else "args": domain}
                    self.env[field.comodel_name].name_search(**domain_arg)

            # Skip the calls related to the attachments and the discussion thread
            # because it reads the same models/fields for all records:
            # `ir.attachment` `search_read`
            # `mail.thread` `message_format`
            # `mail.activity` 'activity_format'
            # controller `/mail/read_followers`

    def mock_view_gantt(self, model, view, fields_list, domain, group_by):
        pass

    def mock_view_graph(self, model, view, fields_list, domain, group_by):
        pass

    def mock_view_grid(self, model, view, fields_list, domain, group_by):
        pass

    def mock_view_kanban(self, model, view, fields_list, domain, group_by):
        kanban_group_by = view.xpath("//kanban")[0].get("default_group_by")
        if kanban_group_by:
            group_by = [*group_by, kanban_group_by]

        if group_by:
            self.mock_web_read_group(model, view, domain, group_by, fields_list, limit_group=10)
        else:
            self.mock_web_search_read(model, view, [domain], fields_list)

        if kanban_group_by:
            for progressbar in view.xpath("//progressbar"):
                bar = {
                    "field": progressbar.get("field"),
                    "colors": literal_eval(progressbar.get("colors")),
                    "sum_field": progressbar.get("sum_field"),
                }
                if (
                    util.version_gte("saas~18.2")
                    and ":" not in kanban_group_by
                    and kanban_group_by in model._fields
                    and model._fields[kanban_group_by].type in ("date, datetime")
                ):
                    kanban_group_by += ":month"
                model.read_progress_bar(domain, kanban_group_by, bar)

    def mock_view_list(self, model, view, fields_list, domain, group_by):
        return self.mock_view_tree(model, view, fields_list, domain, group_by)

    def mock_view_map(self, model, view, fields_list, domain, group_by):
        pass

    def mock_view_pivot(self, model, view, fields_list, domain, group_by):
        pass

    def mock_view_tree(self, model, view, fields_list, domain, group_by):
        if group_by:
            # Limit to 5 the groups to unfold, to avoid fetch the records of all groups, for performance.
            self.mock_web_read_group(model, view, domain, group_by, fields_list, limit_group=5)
        else:
            self.mock_web_search_read(model, view, [domain], fields_list)

    def mock_view_search(self, model, view, action_domain):
        len_search_default = len("search_default_")
        default_filters = [
            (key[len_search_default:], value)
            for key, value in model.env.context.items()
            if key.startswith("search_default_") and value
        ]
        domains = []
        group_bys = []
        for default_filter, value in default_filters:
            for node in view.xpath("//*[@name='{}']".format(default_filter)):
                if node.get("domain"):
                    domains.append(node.get("domain"))
                if node.get("context"):
                    context = literal_eval(node.get("context"))
                    if isinstance(context, dict) and context.get("group_by"):
                        group_bys.append(context["group_by"])
                if node.tag == "field":
                    domains.append("[('{}', '=', {!r})]".format(default_filter, value))

        domains = [self._safe_eval(domain) for domain in domains]
        if action_domain:
            domains = [self._safe_eval(action_domain) if isinstance(action_domain, str) else action_domain, *domains]
        domains = [domain for domain in domains if domain]
        return AND(domains) if domains else [], group_bys

    def mock_web_search_read(self, model, view, domains, fields_list, limit=80):
        _logger.info("search_read, %s, %s", model, domains)
        relation_fields_to_read = {
            node.get("name"): set() for node in view.xpath("//field") if node.get("widget", "").startswith("many2many")
        }
        for domain in domains:
            data = model.search_read(domain=domain, fields=fields_list, limit=80)
            for fname, values in relation_fields_to_read.items():
                values.update(d for r in data for d in r[fname])
        for fname, values in relation_fields_to_read.items():
            read_display_name(model.env[model._fields[fname].comodel_name].browse(values).sudo())

    def mock_web_read_group(self, model, view, domain, group_by, fields_list, limit=80, limit_group=None):
        if hasattr(model, "web_read_group"):
            _logger.info("web_read_group, %s, %s, %s", model, domain, group_by)
            if util.version_gte("saas~18.2"):
                aggregates = [
                    f"{fname}:{model._fields[fname]._description_aggregator(model.env)}"
                    for fname in fields_list
                    if model._fields[fname]._description_aggregator(model.env)
                ]
                groupby = group_by[0]
                if (
                    ":" not in groupby
                    and groupby in model._fields
                    and model._fields[groupby].type in ("date", "datetime")
                ):
                    groupby += ":month"
                data = model.web_read_group(domain, [groupby], aggregates, limit=limit)["groups"]
            else:
                data = model.web_read_group(domain, fields_list, group_by, limit=limit)["groups"]
        else:
            _logger.info("read_group, %s, %s, %s", model, domain, group_by)
            data = model.read_group(domain, fields_list, group_by, limit=limit)

        if limit_group and data:
            # take samples at regular intervals
            # e.g. for a limit_group of 3 and a list of 10 elements, take indexes 0, 5, and 9
            chunk = math.ceil(len(data) / (limit_group - 1))
            data = data[0:-1:chunk] + [data[-1]]  # noqa: RUF005

        if not util.version_gte("saas~16.3"):
            # Get the display name of all groups explicitly for version before the saas~16.3
            # where display_name values was lazy
            first_groupby = group_by[0]
            fname = first_groupby.split(":")[0]  # e.g. date:day
            field = model._fields[fname]
            if field.comodel_name:
                groups = [group[first_groupby][0] for group in data if group[first_groupby]]
                read_display_name(model.env[field.comodel_name].browse(groups).sudo())

        # Get the data in each group
        for group in data:
            domain = group["__domain"] if "__domain" in group else AND([group["__extra_domain"], domain])
            if len(group_by) > 1:
                self.mock_web_read_group(
                    model,
                    view,
                    domain,
                    group_by[1:],
                    fields_list,
                    limit=limit,
                    limit_group=limit_group,
                )
            else:
                self.mock_web_search_read(model, view, [domain], fields_list)


class datetime_extended(datetime.datetime):
    def to_utc(self):
        return self
