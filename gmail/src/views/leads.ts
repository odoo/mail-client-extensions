import { Lead } from "../models/lead";
import { State } from "../models/state";
import { User } from "../models/user";
import { logEmail } from "../services/log_email";
import { getOdooRecordURL } from "../services/odoo_redirection";
import {
    ActionCall,
    EventResponse,
    Notify,
    OpenLink,
    PushCard,
    registerEventHandler,
    UpdateCard,
} from "../utils/actions";
import {
    Button,
    Card,
    CardSection,
    DecoratedText,
    IconButton,
    LinkButton,
} from "../utils/components";
import { UI_ICONS } from "./icons";
import { getPartnerView } from "./partner";
import { getSearchRecordView } from "./search_records";

async function onLogEmailOnLead(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    const leadId = args.leadId;

    const error = await logEmail(_t, user, leadId, "crm.lead", state.email);
    if (error.code) {
        return new Notify(error.toString(_t));
    }

    await state.email.setLoggingState(user, "crm.lead", leadId);
    return new UpdateCard(getPartnerView(state, _t, user));
}
registerEventHandler(onLogEmailOnLead);

function onEmailAlreradyLoggedOnLead(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): EventResponse {
    return new Notify(_t("Email already logged on the opportunity"));
}
registerEventHandler(onEmailAlreradyLoggedOnLead);

async function onCreateLead(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    const result = await Lead.createLead(user, state.partner, state.email);
    if (!result) {
        return new Notify(_t("Could not create the opportunity"));
    }
    const [lead, partner] = result;
    state.partner = partner;
    state.partner.leads.push(lead);
    state.partner.leadCount += 1;
    return new UpdateCard(getPartnerView(state, _t, user));
}
registerEventHandler(onCreateLead);

function onSearchLeadsClick(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): EventResponse {
    return new PushCard(
        getSearchRecordView(
            state,
            _t,
            "crm.lead",
            _t("Opportunities"),
            _t("Log the email on the opportunity"),
            _t("Email already logged on the opportunity"),
            "revenuesDescription",
            "",
            true,
            state.partner.leads,
        ),
    );
}
registerEventHandler(onSearchLeadsClick);

export function buildLeadsView(state: State, _t: Function, user: User, card: Card) {
    const partner = state.partner;
    if (!partner.leads) {
        // CRM module is not installed
        // otherwise leads should be at least an empty array
        return;
    }

    const leads = [...partner.leads].splice(0, 5);

    const leadsSection = new CardSection();

    const searchButton = new IconButton(
        new ActionCall(state, onSearchLeadsClick),
        UI_ICONS.search,
        _t("Search Opportunities"),
    );

    const title = partner.leadCount
        ? _t("Opportunities (%s)", partner.leadCount)
        : _t("Opportunities");
    const widget = new DecoratedText(
        "",
        "<b>" + title + "</b>",
        undefined,
        undefined,
        searchButton,
    );

    leadsSection.addWidget(widget);

    const createButton = new Button(_t("New"), new ActionCall(state, onCreateLead));
    leadsSection.addWidget(createButton);

    for (let lead of leads) {
        let leadButton = null;
        if (state.email.checkLoggingState("crm.lead", lead.id)) {
            leadButton = new IconButton(
                new ActionCall(state, onEmailAlreradyLoggedOnLead),
                UI_ICONS.email_logged,
                _t("Email already logged on the opportunity"),
            );
        } else {
            leadButton = new IconButton(
                new ActionCall(state, onLogEmailOnLead, {
                    leadId: lead.id,
                }),
                UI_ICONS.email_in_odoo,
                _t("Log the email on the opportunity"),
            );
        }

        leadsSection.addWidget(
            new DecoratedText(
                "",
                lead.name,
                undefined,
                lead.revenuesDescription,
                leadButton,
                new OpenLink(getOdooRecordURL(user, "crm.lead", lead.id)),
            ),
        );
    }

    if (leads.length < partner.leadCount) {
        leadsSection.addWidget(
            new LinkButton(_t("Show all"), new ActionCall(state, onSearchLeadsClick)),
        );
    }

    card.addSection(leadsSection);
}
