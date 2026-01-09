import { State } from "../models/state";
import { User } from "../models/user";
import {
    ActionCall,
    EventResponse,
    PopCard,
    PushCard,
    registerEventHandler,
} from "../utils/actions";
import { Button, Card, CardSection, DecoratedText, TextParagraph } from "../utils/components";

export async function onClearTranslationCache(
    state: State,
    _t: Function,
    user: User,
): Promise<EventResponse> {
    user.translations = undefined;
    user.translationsExpireAt = undefined;
    await user.save();
    return new PopCard();
}
registerEventHandler(onClearTranslationCache);

export function onOpenDebugView(state: State, _t: Function, user: User): EventResponse {
    const section = new CardSection([
        new TextParagraph(_t("Debug zone for development purpose.")),
        new DecoratedText(_t("Odoo Server URL"), user.odooUrl),
        new DecoratedText(_t("Odoo Access Token"), user.odooToken),
        new DecoratedText(_t("Odoo Access Token"), user.odooToken),
        new Button(_t("Clear Translations Cache"), new ActionCall(state, onClearTranslationCache)),
    ]);
    const card = new Card([section]);
    section.setHeader(_t("Debug Zone"));
    return new PushCard(card);
}
registerEventHandler(onOpenDebugView);
