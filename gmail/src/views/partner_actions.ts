import { buildView } from "../views/index";
import { buildSearchPartnerView } from "./search_partner";
import { UI_ICONS } from "./icons";
import { State } from "../models/state";
import { Partner } from "../models/partner";
import { actionCall, notify } from "./helpers";
import { updateCard } from "./helpers";
import { _t } from "../services/translation";
import { logEmail } from "../services/log_email";
import { getOdooRecordURL } from "src/services/odoo_redirection";

function onLogEmail(state: State) {
    const partnerId = state.partner.id;

    if (!partnerId) {
        throw new Error(_t("This contact does not exist in the Odoo database."));
    }

    if (State.checkLoggingState(state.email.messageId, "res.partner", partnerId)) {
        const error = logEmail(partnerId, "res.partner", state.email);
        if (error.code) {
            return notify(error.message);
        }
        State.setLoggingState(state.email.messageId, "res.partner", partnerId);
        return updateCard(buildView(state));
    }
    return notify(_t("Email already logged on the contact"));
}

function onSavePartner(state: State) {
    const partner = Partner.savePartner(state.partner);
    if (partner) {
        state.partner = partner;
        state.partner.isWritable = true;
        state.searchedPartners = null;
        return updateCard(buildView(state));
    }
    return notify(_t("Can not save the contact"));
}

export function onEmailAlreadyLoggedContact(state: State) {
    return notify(_t("Email already logged on the contact"));
}

function onSearchPartner(state: State) {
    state.searchedPartners = [];
    return buildSearchPartnerView(state, state.partner.email, true);
}

export function buildPartnerActionView(state: State, partnerSection: CardSection) {
    const actionButtonSet = CardService.newButtonSet();

    const loggingState = State.getLoggingState(state.email.messageId);
    const isEmailLogged =
        state.partner.id && loggingState["res.partner"].indexOf(state.partner.id) >= 0;

    if (!state.partner.id && state.canCreatePartner) {
        actionButtonSet.addButton(
            CardService.newTextButton()
                .setText(_t("Add to Odoo"))
                .setBackgroundColor("#875a7b")
                .setOnClickAction(actionCall(state, onSavePartner.name)),
        );
    }
    if (state.partner.id) {
        actionButtonSet.addButton(
            CardService.newTextButton()
                .setText(_t("View in Odoo"))
                .setBackgroundColor("#875a7b")
                .setOpenLink(
                    CardService.newOpenLink().setUrl(
                        getOdooRecordURL("res.partner", state.partner.id),
                    ),
                ),
        );
    }
    if (state.partner.id && !isEmailLogged && state.partner.isWritable) {
        actionButtonSet.addButton(
            CardService.newImageButton()
                .setAltText(_t("Log email"))
                .setIconUrl(UI_ICONS.email_in_odoo)
                .setOnClickAction(actionCall(state, onLogEmail.name)),
        );
    }
    if (state.partner.id && isEmailLogged) {
        actionButtonSet.addButton(
            CardService.newImageButton()
                .setAltText(_t("Email already logged on the contact"))
                .setIconUrl(UI_ICONS.email_logged)
                .setOnClickAction(actionCall(state, onEmailAlreadyLoggedContact.name)),
        );
    }

    actionButtonSet.addButton(
        CardService.newImageButton()
            .setAltText(_t("Search contact"))
            .setIconUrl(UI_ICONS.search)
            .setOnClickAction(actionCall(state, onSearchPartner.name)),
    );

    partnerSection.addWidget(actionButtonSet);
}
