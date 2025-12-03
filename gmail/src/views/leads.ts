import { buildView } from "../views/index";
import { updateCard, createKeyValueWidget, actionCall, notify, openUrl } from "./helpers";
import { getOdooServerUrl } from "src/services/app_properties";
import { getOdooRecordURL } from "src/services/odoo_redirection";
import { UI_ICONS } from "./icons";
import { logEmail } from "../services/log_email";
import { _t } from "../services/translation";
import { Lead } from "../models/lead";
import { State } from "../models/state";
import { buildSearchRecordView } from "../views/search_records";

function onLogEmailOnLead(state: State, parameters: any) {
    const leadId = parameters.leadId;

    if (State.checkLoggingState(state.email.messageId, "crm.lead", leadId)) {
        const error = logEmail(leadId, "crm.lead", state.email);
        if (error.code) {
            return notify(error.message);
        }

        State.setLoggingState(state.email.messageId, "crm.lead", leadId);
        return updateCard(buildView(state));
    }
    return notify(_t("Email already logged on the opportunity"));
}

function onEmailAlreradyLoggedOnLead(state: State) {
    return notify(_t("Email already logged on the opportunity"));
}

function onCreateLead(state: State) {
    const result = Lead.createLead(state.partner, state.email);
    if (!result) {
        return notify(_t("Could not create the opportunity"));
    }
    const [lead, partner] = result;
    state.partner = partner;
    state.partner.leads.push(lead);
    state.partner.leadCount += 1;
    return updateCard(buildView(state));
}

function onSearchClick(state: State) {
    return buildSearchRecordView(
        state,
        "crm.lead",
        _t("Opportunities"),
        _t("Log the email on the opportunity"),
        _t("Email already logged on the opportunity"),
        "revenuesDescription",
        "",
        true,
        state.partner.leads,
    );
}

export function buildLeadsView(state: State, card: Card) {
    const odooServerUrl = getOdooServerUrl();
    const partner = state.partner;
    if (!partner.leads) {
        // CRM module is not installed
        // otherwise leads should be at least an empty array
        return;
    }

    const leads = [...partner.leads].splice(0, 5);

    const loggingState = State.getLoggingState(state.email.messageId);

    const leadsSection = CardService.newCardSection();

    const searchButton = CardService.newImageButton()
        .setAltText(_t("Search Opportunities"))
        .setIconUrl(UI_ICONS.search)
        .setOnClickAction(actionCall(state, onSearchClick.name));

    const title = partner.leadCount
        ? _t("Opportunities (%s)", partner.leadCount)
        : _t("Opportunities");
    const widget = CardService.newDecoratedText().setText("<b>" + title + "</b>");
    widget.setButton(searchButton);
    leadsSection.addWidget(widget);

    const createButton = CardService.newTextButton()
        .setText(_t("New"))
        .setOnClickAction(actionCall(state, onCreateLead.name));

    leadsSection.addWidget(createButton);

    for (let lead of leads) {
        let leadButton = null;
        if (loggingState["crm.lead"].indexOf(lead.id) >= 0) {
            leadButton = CardService.newImageButton()
                .setAltText(_t("Email already logged on the opportunity"))
                .setIconUrl(UI_ICONS.email_logged)
                .setOnClickAction(actionCall(state, onEmailAlreradyLoggedOnLead.name));
        } else {
            leadButton = CardService.newImageButton()
                .setAltText(_t("Log the email on the opportunity"))
                .setIconUrl(UI_ICONS.email_in_odoo)
                .setOnClickAction(
                    actionCall(state, onLogEmailOnLead.name, {
                        leadId: lead.id,
                    }),
                );
        }

        leadsSection.addWidget(
            createKeyValueWidget(
                null,
                lead.name,
                null,
                lead.revenuesDescription,
                leadButton,
                getOdooRecordURL("crm.lead", lead.id),
            ),
        );
    }

    if (leads.length < partner.leadCount) {
        leadsSection.addWidget(
            CardService.newTextButton()
                .setText(_t("Show all"))
                .setTextButtonStyle(CardService.TextButtonStyle["BORDERLESS"])
                .setOnClickAction(actionCall(state, onSearchClick.name)),
        );
    }

    card.addSection(leadsSection);
    return card;
}
