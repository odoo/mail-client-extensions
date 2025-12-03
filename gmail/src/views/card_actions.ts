import { onBuildDebugView } from "./debug";
import { State } from "../models/state";
import { resetAccessToken } from "../services/odoo_auth";
import { _t, clearTranslationCache } from "../services/translation";
import { actionCall } from "./helpers";
import { pushToRoot } from "./helpers";
import { buildLoginMainView } from "../views/login";

function onLogout() {
    resetAccessToken();
    clearTranslationCache();
    return pushToRoot(buildLoginMainView());
}

export function buildCardActionsView(card: Card) {
    if (State.isLogged) {
        card.addCardAction(
            CardService.newCardAction()
                .setText(_t("Log out"))
                .setOnClickAction(actionCall(undefined, onLogout.name)),
        );
    }

    card.addCardAction(
        CardService.newCardAction()
            .setText(_t("Debug"))
            .setOnClickAction(actionCall(undefined, onBuildDebugView.name)),
    );
}
