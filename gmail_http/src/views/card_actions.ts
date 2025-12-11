import { State } from "../models/state";
import { User } from "../models/user";
import { ActionCall, EventResponse, PushToRoot, registerEventHandler } from "../utils/actions";
import { Card } from "../utils/components";
import { getLoginMainView } from "../views/login";
import { onOpenDebugView } from "./debug";

async function onLogout(state: State, _t: Function, user: User): Promise<EventResponse> {
    user.odooUrl = undefined;
    user.odooToken = undefined;
    await user.save();
    return new PushToRoot(await getLoginMainView(user));
}
registerEventHandler(onLogout);

export function buildCardActionsView(card: Card, _t: Function) {
    card.addAction(_t("Log out"), new ActionCall(undefined, onLogout));
    card.addAction(_t("Debug"), new ActionCall(undefined, onOpenDebugView));
}
