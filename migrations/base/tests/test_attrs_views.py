from lxml import etree
from psycopg2.extras import Json as PsycopgJson

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class TestAttrsViewsTrueFalseDomains(UpgradeCase):
    def _create(self, name, domain):
        return self.env["ir.ui.view"].create(
            {
                "name": f"test_attrs_views_to_expression_{name}",
                "model": "res.groups",
                "type": "form",
                "arch": f"""<form>
                    <field name="name" attrs="{{'invisible': {domain!r}}}" data-domain="{domain!r}"/>
                </form>""",
            },
        )

    def prepare(self):
        true_domains = [
            # weird ones
            [(None, "!=", None)],
            [(False, "!=", False)],
            [(True, "!=", True)],
            ["!", (None, "=", None)],
            # somehow expected
            [(1.0, "=", 1)],
            [(1, "=", 1.0)],
            [(0, "=", 0)],
            [(0, "=", 0.0)],
        ]
        false_domains = [
            # weird ones
            [(None, "=", None)],
            [(False, "=", False)],
            [(True, "=", True)],
            ["!", (None, "!=", None)],
            # somehow expected
            [(1.0, "=", 0)],
            [(1, "=", 0.0)],
            [(0, "=", 1)],
            [(0, "=", 1.0)],
        ]
        return {
            "true_dom": [self._create(f"_true{i}", domain).id for i, domain in enumerate(true_domains)],
            "false_dom": [self._create(f"_false{i}", domain).id for i, domain in enumerate(false_domains)],
        }

    def check(self, info):
        for x in ["True", "False"]:
            for view in map(self.env["ir.ui.view"].browse, info[f"{x.lower()}_dom"]):
                arch = etree.fromstring(view.arch)
                self.assertEqual(arch.tag, 'form', f"root changed in arch of {view.name}\n{view.arch}")
                elem = arch.find("./field")
                self.assertTrue(elem is not None, f"field element not found in arch of {view.name}\n{view.arch}")
                self.assertEqual(elem.get("invisible", "False"), x, f"invalid value for {view.name}\n{view.arch}")


@change_version("saas~16.5")
class TestAttrsViewsToExpression(UpgradeCase):
    _abstract = False
    maxDiff = None

    def prepare(self):

        # test attributes update
        view_1 = self.env["ir.ui.view"].create(
            {
                "name": "test_attrs_views_to_expression",
                "model": "res.partner",
                "type": "form",
                "arch": """<form>
                    <field name="is_company" invisible="1"/>
                    <field name="active" invisible="1"/>
                    <div class="alert alert-warning oe_edit_only" role="alert" attrs="{'invisible': [('same_vat_partner_id', '=', False)]}">
                    A partner with the same <span><span class="o_vat_label">Tax ID</span></span> already exists (<field name="same_vat_partner_id"/>), are you sure to create a new one?
                    </div>
                    <sheet>
                        <div class="oe_button_box" name="button_box"/>
                        <widget name="web_ribbon" title="Archived" bg_color="text-bg-danger" attrs="{'invisible': [('active', '=', True)]}"/>
                        <field name="comment" invisible="1"/>
                        <field name="parent_name" readonly="0"/>
                        <field name="parent_name" readonly="1" invisible="True"/>
                        <field name="parent_name" readonly="True" invisible="True"/>
                        <field name="parent_name" readonly="0" invisible="True"/>
                        <field name="parent_name" readonly="False" invisible="True"/>
                        <field name="parent_name" attrs="{'readonly': 1}"/>
                        <field name="parent_name" attrs="{'readonly': True}"/>
                        <field name="parent_name" attrs="{'readonly': []}"/> <!-- empty domain equal True -->
                        <field name="parent_name" attrs="{'readonly': 0}"/> <!-- python field has readonly=True -->
                        <field name="parent_name" attrs="{'readonly': False}"/>
                        <field name="date" attrs="{'readonly': 1}"/>
                        <field name="date" attrs="{'readonly': True}"/>
                        <field name="date" attrs="{'readonly': []}"/>
                        <field name="date" attrs="{'readonly': 0}"/> <!-- python field has not readonly=True -->
                        <field name="date" attrs="{'readonly': False}"/>

                        <group>
                            <group>
                                <field name="function" placeholder="e.g. Sales Director"
                                    attrs="{'invisible': [('is_company','=', True)]}"/>
                                <field name="phone" widget="phone"/>
                                <field name="mobile" widget="phone"/>
                                <field name="user_ids" invisible="1"/>
                                <field name="email" widget="email" context="{'gravatar_image': True}" attrs="{
                                    'required': [('user_ids','!=', [])],
                                    'invisible': [('user_ids','=', [])],
                                }"/>
                                <field name="website" string="Website" widget="url" placeholder="e.g. https://www.odoo.com"/>
                                <field name="title" options='{"no_open": True}' placeholder="e.g. Mister"
                                    attrs="{'invisible': [('is_company', '=', True)]}"/>
                                <field name="active_lang_count" invisible="1"/>
                                <field name="lang" attrs="{'invisible': [('active_lang_count', '&lt;=', 1)]}"/>
                                <field name="category_id" widget="many2many_tags" options="{'color_field': 'color', 'no_create_edit': True}"
                                    placeholder='e.g. "B2B", "VIP", "Consulting", ...'/>

                                <field name="category_id">
                                    <tree editable="bottom">
                                        <field name="name" readonly="context.get('stuff')" attrs="{'required': '[(&quot;id&quot;,&quot;&lt;&quot;,parent.id)]', 'invisible': [('id', '=', False)]}"/>
                                    </tree>
                                </field>
                            </group>
                        </group>

                        <notebook colspan="4">
                            <page string="Contacts">
                                <field name="country_id" invisible="1"/>
                                <field name="child_ids" mode="kanban" context="{'default_parent_id': active_id, 'default_country_id': country_id, 'default_lang': lang, 'default_type': 'other'}">
                                    <kanban>
                                        <field name="id" invisible="1"/>
                                        <field name="parent_name" attrs="{'readonly': 0}"/>
                                        <field name="date" attrs="{'readonly': 0}"/>
                                        <field name="color"/>
                                        <field name="title"/>
                                        <field name="phone"/>
                                        <field name="comment"/>
                                        <templates>
                                            <t t-name="kanban-box">
                                                <t t-set="color" t-value="kanban_color(record.color.raw_value)"/>
                                                <div t-att-class="color + (record.title.raw_value == 1 ? ' oe_kanban_color_alert' : '') + ' oe_kanban_global_click'">
                                                    <div class="o_kanban_image">
                                                        <img attrs="{'invisible': [('comment', '=', False)]}" alt="Contact image" t-att-src="kanban_image('res.partner', 'comment', record.id.raw_value)"/>
                                                    </div>
                                                    <div class="oe_kanban_details">
                                                        <div t-if="record.phone.raw_value">Phone: <t t-esc="record.phone.value"/></div>
                                                    </div>
                                                    <field name="parent_name" attrs="{'readonly': 0}"/> <!-- python field has readonly=True -->
                                                    <field name="date" attrs="{'readonly': 0}"/> <!-- python field has not readonly=True -->
                                                </div>
                                            </t>
                                        </templates>
                                    </kanban>
                                    <tree editable="bottom">
                                        <field name="is_company" invisible="1"/>
                                        <field name="function" invisible="context.get('stuff')"/>
                                        <field name="phone"/>
                                        <field name="street"
                                            invisible="context.get('stuff')"
                                            attrs="{
                                                'invisible': &quot;[('is_company', '=', parent.is_company)]&quot;,
                                                'readonly': [('phone', 'ilike', '000')],
                                                'required': [('is_company', '=', True), ('phone', 'like', '000')]
                                            }"/>
                                        <field name="street2"/>
                                        <field name="zip"/>
                                        <field name="city"/>
                                    </tree>
                                    <form string="Contact / Address">
                                        <sheet>
                                            <group>
                                                <group>
                                                    <field name="is_company" invisible="1"/>
                                                    <field name="function" invisible="context.get('stuff')"/>
                                                    <field name="phone"/>
                                                    <field name="street"
                                                        invisible="context.get('stuff')"
                                                        attrs="{
                                                            'invisible': &quot;[('is_company', '=', parent.is_company)]&quot;,
                                                            'readonly': [('phone', 'ilike', '000')],
                                                            'required': [('is_company', '=', True), ('phone', 'like', '000')],
                                                        }"/>
                                                    <field name="street2"/>
                                                    <field name="zip"/>
                                                    <field name="city"/>
                                                </group>
                                            </group>
                                        </sheet>
                                    </form>
                                </field>
                            </page>
                        </notebook>
                    </sheet>
                </form>""",
                "priority": 10,
            },
        )

        inherit_1_1 = self.env["ir.ui.view"].create(
            {
                "name": "test_attrs_views_to_expression_inherit",
                "model": "res.partner",
                "type": "form",
                "mode": "extension",
                "inherit_id": view_1.id,
                "arch": """<data>
                    <widget name="web_ribbon" position="after">
                        <field name="id" attrs="{'invisible': [('id', '!=', False)]}"/>
                    </widget>
                    <widget name="web_ribbon" position="replace">
                        <field name="tz_offset"/> 
                    </widget>
                    <field name="tz_offset" position="attributes">
                        <attribute name="readonly">not context.get('toto')</attribute>
                        <attribute name="attrs">{'readonly': [('id', '&lt;', 42)]}</attribute>
                        <!-- log a not found, because an xpath replaced this node in the current view -->
                    </field>
                    <field name="name" position="before">
                        <field name="active" invisible="1"/>
                    </field>
                    <field name="name" position="attributes">
                        <attribute name="readonly">not context.get('test')</attribute>
                        <attribute name="attrs">{'invisible': [('id', '=', 42)]}</attribute>
                        <attribute name="required">context.get('test')</attribute>
                        <!-- if invisible should replace the previous value -->
                        <!-- if readonly should replace the previous value -->
                        <!-- if required should be combine (' or ') with the previous value -->
                    </field>
                    <xpath expr="//field[@name='category_id']//field[@name='name']" position="after">
                        <field name="parent_path" attrs="{}"/>
                    </xpath>
                    <notebook position="inside">
                        <page name="Truc" string="Truc" attrs="{'invisible': [('id', '!=', False)]}">
                            <group>
                                <field name="name" readonly="1"/>
                            </group>
                        </page>
                    </notebook>
                </data>""",
            },
        )

        # check conversion order for inherited views
        inherit_1_2 = self.env["ir.ui.view"].create(
            {
                "name": "test_attrs_views_to_expression_inherit_2",
                "model": "res.partner",
                "type": "form",
                "mode": "extension",
                "inherit_id": view_1.id,
                "arch": """<data>
                    <xpath expr="//field[@name='category_id']//field[@name='name']" position="replace">
                        <field name="id"/>
                    </xpath>
                    <field name="id" position="replace">
                        <!-- should not have not found log, the previous change is applied -->
                        <field name="color"/>
                    </field>
                    <notebook colspan="4" position="inside">
                        <!-- test -->
                        <page string="Test_a" name="test_a" invisible="1" groups="base.group_system" attrs="{'invisible': [('employee', '=', True)]}">
                            <field name="employee" invisible="1"/>
                            <group name="test_group_a"/>
                        </page>
                    </notebook>
                    <page name="test_a" position="attributes">
                        <!-- if log a not found: the converted inerited view 'test_attrs_views_to_expression_inherit' is missing -->
                        <attribute name="readonly">1</attribute>
                    </page>
                </data>""",
            },
        )

        # test if script applied inherit spec by spec and avoid to unactive view
        inherit_1_fail = self.env["ir.ui.view"].create(
            {
                "name": "test_attrs_views_to_expression_inherit_fail",
                "model": "res.partner",
                "type": "form",
                "mode": "extension",
                "inherit_id": view_1.id,
                "arch": """<data>
                    <field name="color" position="attributes">
                        <attribute name="readonly">context.get('no_fail')</attribute>
                    </field>
                </data>""",
            },
        )
        self.env.cr.execute(f"""SELECT arch_db FROM ir_ui_view WHERE id={inherit_1_fail.id}""")
        arch_db = self.env.cr.fetchall()[0][0]
        is_json_translated_field = not isinstance(arch_db, str)

        inherit_1_fail_template = """<data>
                    <field name="color" position="attributes">
                        <attribute name="readonly">context.get('no_fail')</attribute>
                    </field>
                    <kanban position="attributes">
                        <attribute name="js_class">yolo</attribute>
                        <attribute name="attrs">{}</attribute>
                    </kanban>
                    <notebook missing_attribute="True" position="inside">
                        <!-- test -->
                        text abc ---
                        <page string="Test_b" attrs="{'invisible': [('active', '=', True)]}">
                            <field name="active" invisible="context.get('fail')"/>
                        </page>
                    </notebook>
                    <missing position="attributes">
                        <attribute name="readonly">context.get('fail')</attribute>
                        <!-- test -> <- comment -->
                    </missing>
                    <kanban position="replace"/>
                </data>"""
        self.env.cr.execute("""
                UPDATE ir_ui_view
                SET arch_db=%(arch_db)s,
                    active=%(active)s
                WHERE id=%(id)s
            """, {
                'arch_db': PsycopgJson({'en_US': inherit_1_fail_template}) if is_json_translated_field else inherit_1_fail_template,
                'active': True,
                'id': inherit_1_fail.id,
            })

        # test attributes combine (attrs, states, invisible)
        view_2 = self.env["ir.ui.view"].create(
            {
                "name": "test_states",
                "model": "ir.module.module",
                "type": "form",
                "arch": """<form>
                    <field name="state" invisible="1"/>
                    <field name="name" invisible="context.get('a-b')" states="manual" attrs="{'invisible': [('id', '!=', False)]}"/>
                </form>""",
            },
        )

        # test upgrade order with inherited views when use priority and target an extension (must use the inherited relation)
        view_3 = self.env["ir.ui.view"].create(
            {
                "name": "test_attrs_views_order_1",
                "model": "res.partner",
                "type": "form",
                "arch": """<form>
                    <field name="is_company" attrs="{'readonly': [('is_company', '=', True)]}"/>
                </form>""",
                "priority": 10,
            },
        )
        inherit_3_1 = self.env["ir.ui.view"].create(
            {
                "name": "test_attrs_views_order_1_1",
                "model": "res.partner",
                "type": "form",
                "mode": "extension",
                "inherit_id": view_3.id,
                "arch": """<data>
                    <field name="is_company" position="before">
                        <field name="active" invisible="1"/>
                    </field>
                </data>""",
                "priority": 55,
            },
        )
        inherit_3_2 = self.env["ir.ui.view"].create(
            {
                "name": "test_attrs_views_order_1_2",
                "model": "res.partner",
                "type": "form",
                "mode": "extension",
                "inherit_id": inherit_3_1.id,
                "arch": """<data>
                    <field name="is_company" position="after">
                        <field name="name"/>
                    </field>
                    <field name="active" position="before">
                        <field name="id" attrs="{'invisible': [('is_company', '=', True)]}"/>
                    </field>
                </data>""",
                "priority": 1,
            },
        )

        # test upgrade order with inherited views when use priority and target an extension (must use priority)
        view_4 = self.env["ir.ui.view"].create(
            {
                "name": "test_attrs_views_order_2",
                "model": "res.partner",
                "type": "form",
                "arch": """<form>
                    <field name="is_company" attrs="{'readonly': [('is_company', '=', True)]}"/>
                </form>""",
                "priority": 10,
            },
        )
        inherit_4_1 = self.env["ir.ui.view"].create(
            {
                "name": "test_attrs_views_order_2_1",
                "model": "res.partner",
                "type": "form",
                "mode": "extension",
                "inherit_id": view_4.id,
                "arch": """<data>
                    <field name="is_company" position="after">
                        <field name="name" invisible="1"/>
                    </field>
                </data>""",
                "priority": 55,
            },
        )
        self.env["ir.ui.view"].create(
            {
                "name": "test_attrs_views_order_2_2",
                "model": "res.partner",
                "type": "form",
                "mode": "extension",
                "inherit_id": view_4.id,
                "arch": """<data>
                    <field name="is_company" position="before">
                        <field name="child_ids">
                            <tree>
                                <field name="is_company"/>
                            </tree>
                        </field>
                    </field>
                </data>""",
                "priority": 1,
            },
        )
        view_4_primary_1 = self.env["ir.ui.view"].create(
            {
                "name": "test_attrs_views_order_2_1",
                "model": "res.partner",
                "type": "form",
                "mode": "primary",
                "inherit_id": view_4.id,
                "arch": """<data>
                    <field name="name" position="after">
                        <field name="id" invisible="1"/>
                    </field>
                </data>""",
                "priority": 33,
            },
        )

        return {
            'view_1_id': view_1.id,
            'inherit_1_1_id': inherit_1_1.id,
            'inherit_1_2_id': inherit_1_2.id,
            'inherit_1_fail_id': inherit_1_fail.id,
            'view_2_id': view_2.id,
            'inherit_3_2_id': inherit_3_2.id,
            'inherit_4_1_id': inherit_4_1.id,
            'view_4_primary_1_id': view_4_primary_1.id,
        }

    def check(self, data):
        def apply_etree_space(arch):
            return etree.tostring(etree.fromstring(arch), encoding='unicode')

        view_1 = self.env["ir.ui.view"].browse(data['view_1_id'])
        self.assertEqual(apply_etree_space(view_1.arch_db), apply_etree_space("""<form>
                    <field name="is_company" invisible="1"/>
                    <field name="active" invisible="1"/>
                    <div class="alert alert-warning oe_edit_only" role="alert" invisible="not same_vat_partner_id">
                    A partner with the same <span><span class="o_vat_label">Tax ID</span></span> already exists (<field name="same_vat_partner_id"/>), are you sure to create a new one?
                    </div>
                    <sheet>
                        <div class="oe_button_box" name="button_box"/>
                        <widget name="web_ribbon" title="Archived" bg_color="text-bg-danger" invisible="active"/>
                        <field name="comment" invisible="1"/>
                        <field name="parent_name" readonly="0"/>
                        <field name="parent_name" readonly="1" invisible="True"/>
                        <field name="parent_name" readonly="True" invisible="True"/>
                        <field name="parent_name" readonly="0" invisible="True"/>
                        <field name="parent_name" readonly="False" invisible="True"/>
                        <field name="parent_name" readonly="True"/>
                        <field name="parent_name" readonly="True"/>
                        <field name="parent_name" readonly="True"/> <!-- empty domain equal True -->
                        <field name="parent_name" readonly="False"/> <!-- python field has readonly=True -->
                        <field name="parent_name" readonly="False"/>
                        <field name="date" readonly="True"/>
                        <field name="date" readonly="True"/>
                        <field name="date" readonly="True"/>
                        <field name="date"/> <!-- python field has not readonly=True -->
                        <field name="date"/>

                        <group>
                            <group>
                                <field name="function" placeholder="e.g. Sales Director"
                                    invisible="is_company"/>
                                <field name="phone" widget="phone"/>
                                <field name="mobile" widget="phone"/>
                                <field name="user_ids" invisible="1"/>
                                <field name="email" widget="email" context="{'gravatar_image': True}" invisible="not user_ids" required="user_ids"/>
                                <field name="website" string="Website" widget="url" placeholder="e.g. https://www.odoo.com"/>
                                <field name="title" options='{"no_open": True}' placeholder="e.g. Mister"
                                    invisible="is_company"/>
                                <field name="active_lang_count" invisible="1"/>
                                <field name="lang" invisible="active_lang_count &lt;= 1"/>
                                <field name="category_id" widget="many2many_tags" options="{'color_field': 'color', 'no_create_edit': True}"
                                    placeholder='e.g. "B2B", "VIP", "Consulting", ...'/>

                                <field name="category_id">
                                    <tree editable="bottom">
                                        <field name="name" readonly="context.get('stuff')" invisible="not id" required="id &lt; parent.id"/>
                                    </tree>
                                </field>
                            </group>
                        </group>

                        <notebook colspan="4">
                            <page string="Contacts">
                                <field name="country_id" invisible="1"/>
                                <field name="child_ids" mode="kanban" context="{'default_parent_id': active_id, 'default_country_id': country_id, 'default_lang': lang, 'default_type': 'other'}">
                                    <kanban>
                                        <field name="id"/>
                                        <field name="parent_name" />
                                        <field name="date"/>
                                        <field name="color"/>
                                        <field name="title"/>
                                        <field name="phone"/>
                                        <field name="comment"/>
                                        <templates>
                                            <t t-name="kanban-box">
                                                <t t-set="color" t-value="kanban_color(record.color.raw_value)"/>
                                                <div t-att-class="color + (record.title.raw_value == 1 ? ' oe_kanban_color_alert' : '') + ' oe_kanban_global_click'">
                                                    <div class="o_kanban_image">
                                                        <img invisible="not comment" alt="Contact image" t-att-src="kanban_image('res.partner', 'comment', record.id.raw_value)"/>
                                                    </div>
                                                    <div class="oe_kanban_details">
                                                        <div t-if="record.phone.raw_value">Phone: <t t-esc="record.phone.value"/></div>
                                                    </div>
                                                    <field name="parent_name" readonly="False"/> <!-- python field has readonly=True -->
                                                    <field name="date"/> <!-- python field has not readonly=True -->
                                                </div>
                                            </t>
                                        </templates>
                                    </kanban>
                                    <tree editable="bottom">
                                        <field name="is_company" column_invisible="True"/>
                                        <field name="function" column_invisible="context.get('stuff')"/>
                                        <field name="phone"/>
                                        <field name="street"
                                            invisible="is_company == parent.is_company"
                                            column_invisible="context.get('stuff')"
                                            readonly="'000'.lower() in (phone or &quot;&quot;).lower()"
                                            required="is_company and '000' in (phone or &quot;&quot;)"/>
                                        <field name="street2"/>
                                        <field name="zip"/>
                                        <field name="city"/>
                                    </tree>
                                    <form string="Contact / Address">
                                        <sheet>
                                            <group>
                                                <group>
                                                    <field name="is_company" invisible="1"/>
                                                    <field name="function" invisible="context.get('stuff')"/>
                                                    <field name="phone"/>
                                                    <field name="street"
                                                        invisible="context.get('stuff') or is_company == parent.is_company"
                                                        readonly="'000'.lower() in (phone or &quot;&quot;).lower()"
                                                        required="is_company and '000' in (phone or &quot;&quot;)"/>
                                                    <field name="street2"/>
                                                    <field name="zip"/>
                                                    <field name="city"/>
                                                </group>
                                            </group>
                                        </sheet>
                                    </form>
                                </field>
                            </page>
                        </notebook>
                    </sheet>
                </form>"""))
        self.assertTrue(view_1.active)

        inherit_1_1 = self.env["ir.ui.view"].browse(data['inherit_1_1_id'])
        self.assertEqual(apply_etree_space(inherit_1_1.arch_db), apply_etree_space("""<data>
                    <widget name="web_ribbon" position="after">
                        <field name="id" invisible="id"/>
                    </widget>
                    <widget name="web_ribbon" position="replace">
                        <field name="tz_offset"/> 
                    </widget>
                    <field name="tz_offset" position="attributes">
                        <attribute name="readonly">(not context.get('toto')) or (id &lt; 42)</attribute>
                        <!-- log a not found, because an xpath replaced this node in the current view -->
                    </field>
                    <field name="name" position="before">
                        <field name="active" column_invisible="True"/>
                    </field>
                    <field name="name" position="attributes">
                        <attribute name="invisible">id == 42</attribute>
                        <attribute name="readonly">not context.get('test')</attribute>
                        <attribute name="required" add="context.get('test')" separator=" or "/>
                        <!-- if invisible should replace the previous value -->
                        <!-- if readonly should replace the previous value -->
                        <!-- if required should be combine (' or ') with the previous value -->
                    </field>
                    <xpath expr="//field[@name='category_id']//field[@name='name']" position="after">
                        <field name="parent_path"/>
                    </xpath>
                    <notebook position="inside">
                        <page name="Truc" string="Truc" invisible="id">
                            <group>
                                <field name="name" readonly="1"/>
                            </group>
                        </page>
                    </notebook>
                </data>"""))
        self.assertTrue(inherit_1_1.active)

        inherit_1_2 = self.env["ir.ui.view"].browse(data['inherit_1_2_id'])
        self.assertEqual(apply_etree_space(inherit_1_2.arch_db), apply_etree_space("""<data>
                    <xpath expr="//field[@name='category_id']//field[@name='name']" position="replace">
                        <field name="id"/>
                    </xpath>
                    <field name="id" position="replace">
                        <!-- should not have not found log, the previous change is applied -->
                        <field name="color"/>
                    </field>
                    <notebook colspan="4" position="inside">
                        <!-- test -->
                        <page string="Test_a" name="test_a" groups="base.group_system" invisible="1">
                            <field name="employee" invisible="1"/>
                            <group name="test_group_a"/>
                        </page>
                    </notebook>
                    <page name="test_a" position="attributes">
                        <!-- if log a not found: the converted inerited view 'test_attrs_views_to_expression_inherit' is missing -->
                        <attribute name="readonly">1</attribute>
                    </page>
                </data>"""))
        self.assertTrue(inherit_1_2.active)

        inherit_1_fail = self.env["ir.ui.view"].browse(data['inherit_1_fail_id'])
        self.assertEqual(apply_etree_space(inherit_1_fail.arch_db), apply_etree_space("""<data>
                    <field name="color" position="attributes">
                        <attribute name="readonly">context.get('no_fail')</attribute>
                    </field>
                    <kanban position="attributes">
                        <attribute name="js_class">yolo</attribute>
                        </kanban>
                    <notebook missing_attribute="True" position="inside">
                        <!-- test -->
                        text abc ---
                        <page string="Test_b" invisible="active">
                            <field name="active" invisible="context.get('fail')"/>
                        </page>
                    </notebook>
                    <missing position="attributes">
                        <attribute name="readonly">context.get('fail')</attribute>
                        <!-- test -> <- comment -->
                    </missing>
                    <kanban position="replace"/>
                </data>"""))
        self.assertFalse(inherit_1_fail.active)  # disabled by upgrade (can't repair it)

        view_2 = self.env["ir.ui.view"].browse(data['view_2_id'])
        self.assertEqual(apply_etree_space(view_2.arch_db), apply_etree_space("""<form>
                    <field name="state" invisible="1"/>
                    <field name="name" invisible="context.get('a-b') or (id and state != 'manual')"/>
                </form>"""))
        self.assertTrue(view_2.active)

        inherit_3_2 = self.env["ir.ui.view"].browse(data['inherit_3_2_id'])
        self.assertEqual(apply_etree_space(inherit_3_2.arch_db), apply_etree_space("""<data>
                    <field name="is_company" position="after">
                        <field name="name"/>
                    </field>
                    <field name="active" position="before">
                        <field name="id" invisible="is_company"/>
                    </field>
                </data>"""),
                "Miss inheriting order (must use the inherited relation)")
        self.assertTrue(inherit_3_2.active)

        inherit_4_1 = self.env["ir.ui.view"].browse(data['inherit_4_1_id'])
        self.assertEqual(apply_etree_space(inherit_4_1.arch_db), apply_etree_space("""<data>
                    <field name="is_company" position="after">
                        <field name="name" column_invisible="True"/>
                    </field>
                </data>"""),
                "Miss inheriting order (must use priority)")
        self.assertTrue(inherit_4_1.active)

        view_4_primary_1 = self.env["ir.ui.view"].browse(data['view_4_primary_1_id'])
        self.assertEqual(apply_etree_space(view_4_primary_1.arch_db), apply_etree_space("""<data>
                    <field name="name" position="after">
                        <field name="id" column_invisible="True"/>
                    </field>
                </data>"""),
                "Miss inheriting order (mode=primary is applied after all extend mode)")
        self.assertTrue(view_4_primary_1.active)
