import { buildView } from "../views/index";
import { buildSearchPartnerView } from "./search_partner";
import { UI_ICONS } from "./icons";
import { State } from "../models/state";
import { Partner } from "../models/partner";
import { actionCall } from "./helpers";
import { updateCard } from "./helpers";
import { _t } from "../services/translation";
import { buildLoginMainView } from "./login";

function onSearchPartner(state: State) {
    if (!state.searchedPartners) {
        const [partners, error] = Partner.searchPartner(state.partner.email);
        state.searchedPartners = partners;
    }

    return buildSearchPartnerView(state, state.partner.email, true);
}

function onReloadPartner(state: State) {
    [
        state.partner,
        state.odooUserCompanies,
        state.canCreatePartner,
        state.canCreateProject,
        state.error,
    ] = Partner.getPartner(state.partner.email, state.partner.name, state.partner.id);

    return updateCard(buildView(state));
}

export function buildPartnerActionView(state: State, partnerSection: CardSection) {
    const isLogged = State.isLogged;
    const canContactOdooDatabase = state.error.canContactOdooDatabase && isLogged;

    if (canContactOdooDatabase) {
        const actionButtonSet = CardService.newButtonSet();

        if (state.partner.id) {
            actionButtonSet.addButton(
                CardService.newImageButton()
                    .setAltText(_t("Refresh"))
                    .setIconUrl(UI_ICONS.reload)
                    .setOnClickAction(actionCall(state, onReloadPartner.name)),
            );
        }

        actionButtonSet.addButton(
            CardService.newImageButton()
                .setAltText(_t("Search contact"))
                .setIconUrl(UI_ICONS.search)
                .setOnClickAction(actionCall(state, onSearchPartner.name)),
        );

        partnerSection.addWidget(actionButtonSet);
    } else if (!isLogged) {
        // add button but it redirects to the login page
        const actionButtonSet = CardService.newButtonSet();

        actionButtonSet.addButton(
            CardService.newImageButton()
                .setAltText(_t("Search contact"))
                .setIconUrl(UI_ICONS.search)
                .setOnClickAction(actionCall(state, buildLoginMainView.name)),
        );

        partnerSection.addWidget(actionButtonSet);
    }
}
