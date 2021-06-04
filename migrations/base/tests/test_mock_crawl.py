# -*- coding: utf-8 -*-
import logging
import math
from ast import literal_eval
from traceback import format_exception
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import fields
from odoo.exceptions import RedirectWarning, UserError
from odoo.osv import expression
from odoo.tools import mute_logger, table_kind
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import IntegrityCase

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

NS = "odoo.addons.base.maintenance.migrations.base.tests"
_logger = logging.getLogger(NS + __name__)


class TestCrawler(IntegrityCase):
    view_tracebacks = {}

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
        before = value = [tuple(v) for v in value]
        after = self.invariant()

        diff = []
        for a in after:
            for i in range(len(a)):
                if a[i] in [b[i] for b in before]:
                    break
            else:
                if self.env["ir.ui.menu"].browse(a[1]).sudo().create_date.date() == fields.date.today():
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

    def invariant(self):

        self.action_type_fields = {
            action_type: list(self.env.registry[action_type]._fields)
            for action_type in list(self.env.registry["ir.actions.actions"]._inherit_children) + ["ir.actions.actions"]
        }

        # Try to use an admin to crawl the menus, if not fallback on using an employee.
        for group in ["base.group_system", "base.group_erp_manager", "base.group_user"]:
            user = (
                self.env["res.users"].sudo().search([("groups_id", "in", self.env.ref(group).id)], order="id", limit=1)
            )
            if user:
                self.env = self.env(user=user)
                break

        if hasattr(self.env, "companies"):
            self.env = self.env(context=dict(self.env.context, allowed_company_ids=[self.env.user.company_id.id]))

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
                lambda s, v, r, validate=True: origin_reference_convert_to_cache(s, v, r, False),
            ):
                _logger.info("Mocking menus with user %s(#%s) ", self.env.user.login, self.env.user.id)
                root = self.env["ir.ui.menu"].load_menus(debug=False)
                for menu in root["children"]:
                    failing.update(self.crawl_menu(menu))

        return list(failing)

    def _safe_eval(self, value):
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
        # JS Framework added a non standard `to_utc` method on datetime
        # e.g. `datetime.datetime.combine(context_today(), datetime.time(0,0,0)).to_utc()`
        # Can't directly patch `to_utc` to existing `datetime.datetime`:
        # `TypeError: can't set attributes of built-in/extension type 'datetime.datetime'`
        # https://stackoverflow.com/a/4482067
        with patch(to_patch, datetime_extended):
            return safe_eval(value, eval_context)

    def crawl_menu(self, menu, parent=None):
        menu_name = "%s > %s" % (parent, menu["name"]) if parent else menu["name"]
        _logger.info("Mocking menu %s", menu_name)
        failing = set()
        if menu.get("action"):
            action_id = int(menu["action"].split(",")[1])
            action = self.env["ir.actions.actions"].browse(action_id)
            try:
                action_typed = self.env[action.type].browse(action_id)
                [action_vals] = action_typed.read(self.action_type_fields[action.type])
                self.mock_action(action_vals)
            except Exception as e:
                self.env.cr.rollback()  # In case the cursor is broken
                failing_menu = (menu["xmlid"], menu["id"], menu_name, action_id)
                self.view_tracebacks[failing_menu] = " ".join(format_exception(type(e), e, e.__traceback__))
                _logger.exception("Adding menu %s to the failing menus", failing_menu)
                failing.add(failing_menu)
        for child in menu.get("children"):
            failing.update(self.crawl_menu(child, menu_name))
        return failing

    def mock_action(self, action):
        if action["type"] == "ir.actions.act_window":
            pass
        elif action["type"] == "ir.actions.server":
            try:
                action = self.env[action["type"]].browse(action["id"]).run()
            except UserError:
                # Ignore, in the web client, it would only display a warning dialog
                # e.g. in 13.0, Accounting > Configuration > Payments > Add a Bank Account
                # triggering `setting_init_bank_account_action` of `account_online_sync/models/company.py`
                # raising a UserError to tell the user he must create a bank journal if he has not one yet.
                return
            except RedirectWarning as redirect:
                # Action can redirect to another with a message.
                # e.g. in 14.0, the method `setting_init_bank_account_action` of `account_online_sync/models/company.py`
                # now raise a `RedirectWarning`.
                action_id = redirect.args[1]
                action_type = self.env["ir.actions.actions"].browse(action_id).type
                [action] = self.env[action_type].browse(action_id).read(self.action_type_fields[action_type])

            return self.mock_action(action)
        elif action["type"] in ("ir.actions.client", "ir.actions.act_url"):
            return
        else:
            _logger.error("Action %s is not implemented", action["type"])
            return

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

        Action = env.registry["ir.actions.actions"]
        origin_read = Action.read
        action_fields = self.action_type_fields["ir.actions.actions"]
        # To specify the list of fields to read on actions,
        # because `get_bindings` calls read without passing the list fields,
        # and it therefore reads alls the fields, and some custom fields might be broken.
        with patch.object(
            Action,
            "read",
            lambda self, *args, **kwargs: origin_read(self, fields=action_fields),
        ):
            views = model.load_views(
                action["views"], options={"action_id": action.get("id"), "toolbar": True, "load_filters": True}
            )
        env["ir.filters"].get_filters(model._name, action_id=action.get("id"))

        domain, group_by = [], []
        if "search_view" in action:
            view = etree.fromstring(literal_eval(action["search_view"])["arch"])
            domain, group_by = self.mock_view_search(model, view, action["domain"])

        kind_of_table = table_kind(self.env.cr, model._table)
        if not kind_of_table:
            # Dashboard module: a menu / action without table or view.
            pass
        elif kind_of_table in ("v", "m") and any(field.manual for field in model._fields.values()):
            # Report SQL views with custom columns.
            _logger.warning(
                "Mocking of model %s skipped because it is based on an SQL view with custom columns. "
                "This is only possible with a custom module or a very technical manual intervention.",
                model._name,
            )
        else:
            for view_type, data in views["fields_views"].items():
                mock_method = getattr(self, "mock_view_%s" % view_type, None)
                if mock_method:
                    _logger.info("Mocking view %s: %s", view_type, data["name"])
                    fields_list = list(data["fields"])
                    view = etree.fromstring(data["arch"])
                    mock_method(model, view, fields_list, domain, group_by)

    def mock_view_activity(self, model, view, fields_list, domain, group_by):
        domain = expression.AND([domain, [("activity_ids", "!=", False)]])
        self.env["mail.activity"].get_activity_data(model._name, domain)

    def mock_view_calendar(self, model, view, fields_list, domain, group_by):
        pass

    def mock_view_cohort(self, model, view, fields_list, domain, group_by):
        pass

    def mock_view_dashboard(self, model, view, fields_list, domain, group_by):
        pass

    def mock_view_form(self, model, view, fields_list, domain, group_by):
        relation_fields_to_read = {
            node.get("name") for node in view.xpath("//field") if node.get("widget", "").startswith("many2many_")
        }
        records = model.search(domain, limit=3)
        _logger.info("view_form, %s, %s", records, domain)
        for i in range(len(records)):
            # `records[i]` is to exactly mimic the web client.
            # `for record in records` would prefetch the fields of all the records
            # and not one by one as a form view would do.
            record = records[i]
            [data] = record.read(fields_list)
            for fname in relation_fields_to_read:
                model.env[model._fields[fname].comodel_name].browse(data[fname]).sudo().name_get()

            processed_data = {}
            for fname, value in data.items():
                if fname in model._fields and model._fields[fname].type == "many2one" and value:
                    value = value[0]
                processed_data[fname] = value

            for node in view.xpath("//field[@widget='statusbar']"):
                fname = node.get("name")
                field = model._fields[fname]
                if field.comodel_name:

                    domain = []
                    if node.get("domain"):
                        domain = [("id", "=", processed_data[fname])] if processed_data[fname] else []
                        domain = expression.OR(
                            [domain, safe_eval(node.get("domain"), dict(uid=self.env.user.id, **processed_data))]
                        )

                    fields_to_read = ["id"]
                    if node.get("options"):
                        options = literal_eval(node.get("options"))
                        if options.get("fold_field"):
                            fields_to_read.append(options["fold_field"])

                    values = self.env[field.comodel_name].search_read(domain, fields_to_read)
                    self.env[field.comodel_name].browse([value["id"] for value in values]).name_get()

            for node in view.xpath("//field[@widget='selection']"):
                fname = node.get("name")
                field = model._fields[fname]
                if field.comodel_name:
                    domain = []
                    if node.get("domain"):
                        domain = safe_eval(node.get("domain"), dict(uid=self.env.user.id, **processed_data))
                    self.env[field.comodel_name].name_search(args=domain)

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
            group_by = group_by + [kanban_group_by]

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
            for node in view.xpath("//*[@name='%s']" % default_filter):
                if node.get("domain"):
                    domains.append(node.get("domain"))
                if node.get("context"):
                    context = literal_eval(node.get("context"))
                    if isinstance(context, dict) and context.get("group_by"):
                        group_bys.append(context["group_by"])
                if node.tag == "field":
                    domains.append("[('%s', '=', %r)]" % (default_filter, value))

        domains = [self._safe_eval(domain) for domain in domains]
        if action_domain:
            domains = [self._safe_eval(action_domain) if isinstance(action_domain, str) else action_domain] + domains
        domains = [domain for domain in domains if domain]
        return expression.AND(domains) if domains else [], group_bys

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
            model.env[model._fields[fname].comodel_name].browse(values).sudo().name_get()

    def mock_web_read_group(self, model, view, domain, group_by, fields_list, limit=80, limit_group=None):
        _logger.info("read_group, %s, %s, %s", model, domain, group_by)
        if hasattr(model, "web_read_group"):
            data = model.web_read_group(domain, fields_list, group_by, limit=limit)["groups"]
        else:
            data = model.read_group(domain, fields_list, group_by, limit=limit)

        if limit_group and data:
            # take samples at regular intervals
            # e.g. for a limit_group of 3 and a list of 10 elements, take indexes 0, 5, and 9
            chunk = math.ceil(len(data) / (limit_group - 1))
            data = data[0:-1:chunk] + [data[-1]]

        # Get the display name of all groups
        group_by = group_by[0]
        fname = group_by.split(":")[0]  # e.g. date:day
        field = model._fields[fname]
        if field.comodel_name:
            groups = [group[group_by][0] for group in data if group[group_by]]
            model.env[field.comodel_name].browse(groups).sudo().name_get()

        # Get the data in each group
        for group in data:
            if group.get("__context", {}).get("group_by"):
                self.mock_web_read_group(
                    model,
                    view,
                    group["__domain"],
                    group["__context"]["group_by"],
                    fields_list,
                    limit=limit,
                    limit_group=limit_group,
                )
            else:
                self.mock_web_search_read(model, view, [group["__domain"]], fields_list)


class datetime_extended(datetime.datetime):
    def to_utc(self):
        return self
