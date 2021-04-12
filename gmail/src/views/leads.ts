import { buildView } from "../views/index";
import { pushCard, updateCard, createKeyValueWidget, actionCall, notify, openUrl } from "./helpers";
import { URLS } from "../const";
import { UI_ICONS } from "./icons";
import { logEmail } from "../services/log_email";
import { _t } from "../services/translation";
import { Lead } from "../models/lead";
import { State } from "../models/state";

function onLogEmailOnLead(state: State, parameters: any) {
    const emailBody = state.email.body;
    const leadId = parameters.leadId;

    if (State.setLoggingState(state.email.messageId, "leads", leadId)) {
        logEmail(leadId, "crm.lead", emailBody);
        return updateCard(buildView(state));
    }
    return notify(_t("Email already logged on the lead"));
}

function onEmailAlreradyLoggedOnLead(state: State) {
    return notify(_t("Email already logged on the lead"));
}

function onCreateLead(state: State) {
    const leadId = Lead.createLead(state.partner.id, state.email.body, state.email.subject);

    if (!leadId) {
        return notify(_t("Could not create the lead"));
    }

    const leadUrl =
        State.odooServerUrl +
        `/web#id=${leadId}&action=crm_mail_plugin.crm_lead_action_form_edit&model=crm.lead&view_type=form`;

    return openUrl(leadUrl);
}

export function buildLeadsView(state: State, card: Card) {
    const odooServerUrl = State.odooServerUrl;
    const partner = state.partner;
    const leads = partner.leads;

    if (!leads) {
        // CRM module is not installed
        // otherwise leads should be at least an empty array
        return;
    }

    const loggingState = State.getLoggingState(state.email.messageId);

    const leadsSection = CardService.newCardSection().setHeader(
        "<b>" + _t("Opportunities (%s)", leads.length) + "</b>",
    );

    if (state.partner.id) {
        leadsSection.addWidget(
            CardService.newTextButton().setText(_t("Create")).setOnClickAction(actionCall(state, "onCreateLead")),
        );

        for (let lead of leads) {
            let leadRevenuesDescription;
            if (lead.recurringRevenue) {
                leadRevenuesDescription = _t(
                    "%(expected_revenue)s + %(recurring_revenue)s %(recurring_plan)s at %(probability)s%",
                    {
                        expected_revenue: lead.expectedRevenue,
                        probability: lead.probability,
                        recurring_revenue: lead.recurringRevenue,
                        recurring_plan: lead.recurringPlan,
                    },
                );
            } else {
                leadRevenuesDescription = _t("%(expected_revenue)s at %(probability)s%", {
                    expected_revenue: lead.expectedRevenue,
                    probability: lead.probability,
                });
            }

            let leadButton = null;
            if (loggingState["leads"].indexOf(lead.id) >= 0) {
                leadButton = CardService.newImageButton()
                    .setAltText(_t("Email already logged on the lead"))
                    .setIconUrl(UI_ICONS.email_logged)
                    .setOnClickAction(actionCall(state, "onEmailAlreradyLoggedOnLead"));
            } else {
                leadButton = CardService.newImageButton()
                    .setAltText(_t("Log the email on the lead"))
                    .setIconUrl(UI_ICONS.email_in_odoo)
                    .setOnClickAction(
                        actionCall(state, "onLogEmailOnLead", {
                            leadId: lead.id,
                        }),
                    );
            }

            leadsSection.addWidget(
                createKeyValueWidget(
                    null,
                    lead.name,
                    null,
                    leadRevenuesDescription,
                    leadButton,
                    odooServerUrl + `/web#id=${lead.id}&model=crm.lead&view_type=form`,
                ),
            );
        }
    } else {
        leadsSection.addWidget(CardService.newTextParagraph().setText(_t("Save Contact to create new Opportunities.")));
    }

    card.addSection(leadsSection);
    return card;
}
