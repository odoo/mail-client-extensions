import { buildView } from "./index";
import { buildLeadsView } from "./leads";
import { buildTicketsView } from "./tickets";
import { buildPartnerActionView } from "./partner_actions";
import { updateCard } from "./helpers";
import { UI_ICONS } from "./icons";
import { createKeyValueWidget, actionCall, notify } from "./helpers";
import { URLS } from "../const";
import { State } from "../models/state";
import { Partner } from "../models/partner";
import { ErrorMessage } from "../models/error_message";
import { logEmail } from "../services/log_email";

function onEnrichCompany(state: State) {
    const [company, error] = Partner.enrichCompany(state.partner.id);
    state.partner.company = company;
    state.error = error;
    return updateCard(buildView(state));
}

function onLogEmail(state: State) {
    const emailBody = state.email.body;
    const partnerId = state.partner.id;

    if (!partnerId) {
        throw new Error("This contact does not exist in the Odoo database.");
    }

    if (State.setLoggingState(state.email.messageId, "partners", partnerId)) {
        logEmail(partnerId, "res.partner", emailBody);
        return updateCard(buildView(state));
    }
    return notify("Email already logged on the contact");
}

function onSavePartner(state: State) {
    const partnerValues = {
        name: state.partner.name,
        email: state.partner.email,
        company: state.partner.company && state.partner.company.id,
    };

    const partnerId = Partner.savePartner(partnerValues);
    if (partnerId) {
        state.partner.id = partnerId;
        state.searchedPartners = null;
        state.error = new ErrorMessage();
        return updateCard(buildView(state));
    } else {
        return notify("Can not save the contact");
    }
}

function onEmailAlreadyLogged(state: State) {
    return notify("Email already logged on the contact");
}

export function buildPartnerView(state: State, card: Card) {
    const partner = state.partner;
    const odooServerUrl = State.odooServerUrl;
    const canContactOdooDatabase = state.error.canContactOdooDatabase && State.isLogged;

    const loggingState = State.getLoggingState(state.email.messageId);
    const isEmailLogged = partner.id && loggingState["partners"].indexOf(partner.id) >= 0;

    const partnerSection = CardService.newCardSection().setHeader("<b>Contact</b>");

    let partnerButton = null;
    if (canContactOdooDatabase && !partner.id) {
        partnerButton = CardService.newImageButton()
            .setAltText("Save in Odoo")
            .setIconUrl(UI_ICONS.save_in_odoo)
            .setOnClickAction(actionCall(state, "onSavePartner"));
    } else if (canContactOdooDatabase && !isEmailLogged) {
        partnerButton = CardService.newImageButton()
            .setAltText("Log email")
            .setIconUrl(UI_ICONS.email_in_odoo)
            .setOnClickAction(actionCall(state, "onLogEmail"));
    } else if (canContactOdooDatabase && isEmailLogged) {
        partnerButton = CardService.newImageButton()
            .setAltText("Email already logged on the contact")
            .setIconUrl(UI_ICONS.email_logged)
            .setOnClickAction(actionCall(state, "onEmailAlreadyLogged"));
    } else if (!State.isLogged) {
        // button "Log the email" but it redirects to the login page
        partnerButton = CardService.newImageButton()
            .setAltText("Log email")
            .setIconUrl(UI_ICONS.email_in_odoo)
            .setOnClickAction(actionCall(state, "buildLoginMainView"));
    }

    const partnerContent = [partner.email, partner.phone]
        .filter((x) => x)
        .map((x) => `<font color="#777777">${x}</font>`);

    const partnerCard = createKeyValueWidget(
        null,
        partner.name + "<br>" + partnerContent.join("<br>"),
        partner.image || UI_ICONS.person,
        null,
        partnerButton,
        partner.id
            ? odooServerUrl + `/web#id=${partner.id}&model=res.partner&view_type=form`
            : canContactOdooDatabase
            ? null
            : actionCall(state, "buildLoginMainView"),
        false,
        partner.email,
    );

    partnerSection.addWidget(partnerCard);

    buildPartnerActionView(state, partnerSection);

    card.addSection(partnerSection);

    if (canContactOdooDatabase) {
        buildLeadsView(state, card);
        buildTicketsView(state, card);
    }

    return card;
}
