import { buildPartnerView } from "./partner";
import { buildErrorView } from "./error";
import { buildCompanyView } from "./company";
import { buildLoginMainView } from "./login";
import { buildCardActionsView } from "./card_actions";
import { State } from "../models/state";
import { actionCall } from "./helpers";

export function buildView(state: State) {
    const card = CardService.newCardBuilder();

    if (state.error.code) {
        buildErrorView(state, card);
    }

    buildPartnerView(state, card);

    buildCompanyView(state, card);

    buildCardActionsView(state, card);

    if (!State.isLogged) {
        card.setFixedFooter(
            CardService.newFixedFooter().setPrimaryButton(
                CardService.newTextButton()
                    .setText("Login")
                    .setBackgroundColor("#00A09D")
                    .setOnClickAction(actionCall(state, "buildLoginMainView")),
            ),
        );
    }

    return card.build();
}
