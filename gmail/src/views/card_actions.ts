import { buildView } from "../views/index";
import { State } from "../models/state";
import { Partner } from "../models/partner";
import { resetAccessToken } from "../services/odoo_auth";
import { _t, clearTranslationCache } from "../services/translation";
import { actionCall } from "./helpers";
import { pushToRoot } from "./helpers";

function onLogout(state: State) {
    resetAccessToken();
    clearTranslationCache();

    const [partner, odooUserCompanies, error] = Partner.enrichPartner(
        state.email.contactEmail,
        state.email.contactName,
    );
    const newState = new State(partner, state.email, odooUserCompanies, null, null, error);
    return pushToRoot(buildView(newState));
}

export function buildCardActionsView(state: State, card: Card) {
    const canContactOdooDatabase = state.error.canContactOdooDatabase && State.isLogged;

    if (State.isLogged) {
        card.addCardAction(
            CardService.newCardAction().setText(_t("Logout")).setOnClickAction(actionCall(state, "onLogout")),
        );
    }

    card.addCardAction(
        CardService.newCardAction().setText(_t("Debug")).setOnClickAction(actionCall(state, "buildDebugView")),
    );
}
