function onLogEmailOnLead(state, parameters) {
    var leadId = parameters.leadId;
    if (State.checkLoggingState(state.email.messageId, "leads", leadId)) {
        state.error = (0, logEmail)(leadId, "crm.lead", state.email);
        if (!state.error.code) {
            State.setLoggingState(state.email.messageId, "leads", leadId);
        }
        return (0, updateCard)((0, buildView)(state));
    }
    return (0, notify)((0, _t)("Email already logged on the lead"));
}
function onEmailAlreradyLoggedOnLead(state) {
    return (0, notify)((0, _t)("Email already logged on the lead"));
}
function onCreateLead(state) {
    var leadId = Lead.createLead(state.partner.id, state.email.body, state.email.subject);
    if (!leadId) {
        return (0, notify)((0, _t)("Could not create the lead"));
    }
    var cids = state.odooCompaniesParameter;
    var leadUrl =
        State.odooServerUrl +
        "/web#id="
            .concat(leadId, "&action=crm_mail_plugin.crm_lead_action_form_edit&model=crm.lead&view_type=form")
            .concat(cids);
    return (0, openUrl)(leadUrl);
}
function buildLeadsView(state, card) {
    var odooServerUrl = State.odooServerUrl;
    var partner = state.partner;
    var leads = partner.leads;
    if (!leads) {
        // CRM module is not installed
        // otherwise leads should be at least an empty array
        return;
    }
    var loggingState = State.getLoggingState(state.email.messageId);
    var leadsSection = CardService.newCardSection().setHeader(
        "<b>" + (0, _t)("Opportunities (%s)", leads.length) + "</b>",
    );
    var cids = state.odooCompaniesParameter;
    if (state.partner.id) {
        leadsSection.addWidget(
            CardService.newTextButton()
                .setText((0, _t)("Create"))
                .setOnClickAction((0, actionCall)(state, "onCreateLead")),
        );
        for (var _i = 0, leads_1 = leads; _i < leads_1.length; _i++) {
            var lead = leads_1[_i];
            var leadRevenuesDescription = void 0;
            if (lead.recurringRevenue) {
                leadRevenuesDescription = (0, _t)(
                    "%(expected_revenue)s + %(recurring_revenue)s %(recurring_plan)s at %(probability)s%",
                    {
                        expected_revenue: lead.expectedRevenue,
                        probability: lead.probability,
                        recurring_revenue: lead.recurringRevenue,
                        recurring_plan: lead.recurringPlan,
                    },
                );
            } else {
                leadRevenuesDescription = (0, _t)("%(expected_revenue)s at %(probability)s%", {
                    expected_revenue: lead.expectedRevenue,
                    probability: lead.probability,
                });
            }
            var leadButton = null;
            if (loggingState["leads"].indexOf(lead.id) >= 0) {
                leadButton = CardService.newImageButton()
                    .setAltText((0, _t)("Email already logged on the lead"))
                    .setIconUrl(UI_ICONS.email_logged)
                    .setOnClickAction((0, actionCall)(state, "onEmailAlreradyLoggedOnLead"));
            } else {
                leadButton = CardService.newImageButton()
                    .setAltText((0, _t)("Log the email on the lead"))
                    .setIconUrl(UI_ICONS.email_in_odoo)
                    .setOnClickAction(
                        (0, actionCall)(state, "onLogEmailOnLead", {
                            leadId: lead.id,
                        }),
                    );
            }
            leadsSection.addWidget(
                (0, createKeyValueWidget)(
                    null,
                    lead.name,
                    null,
                    leadRevenuesDescription,
                    leadButton,
                    odooServerUrl + "/web#id=".concat(lead.id, "&model=crm.lead&view_type=form").concat(cids),
                ),
            );
        }
    } else if (state.canCreatePartner) {
        leadsSection.addWidget(
            CardService.newTextParagraph().setText((0, _t)("Save Contact to create new Opportunities.")),
        );
    } else {
        leadsSection.addWidget(
            CardService.newTextParagraph().setText(
                (0, _t)("You can only create opportunities for existing customers."),
            ),
        );
    }
    card.addSection(leadsSection);
    return card;
}
