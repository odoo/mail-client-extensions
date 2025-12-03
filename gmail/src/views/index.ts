import { buildPartnerView } from "./partner";
import { buildCardActionsView } from "./card_actions";
import { buildSearchPartnerView } from "./search_partner";
import { State } from "../models/state";
import { _t } from "../services/translation";

export function buildView(state: State) {
    const card = CardService.newCardBuilder();
    if (state.searchedPartners?.length) {
        return buildSearchPartnerView(state, "", false, _t("In this conversation"), true, true);
    } else {
        buildPartnerView(state, card);
    }

    return card.build();
}
