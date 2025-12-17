/**
 * Build the JSON format to execute action (like updating a cart, showing a notification,...)
 *
 * https://developers.google.com/workspace/add-ons/guides/alternate-runtimes
 */
import jwt from "jsonwebtoken";
import { HOST } from "../consts";
import { State } from "../models/state";
import { User } from "../models/user";
import { Card } from "./components";

/**
 * Class used to respond to an event
 * (like pushing a card, showing a notification, redirecting to an url...).
 */
export abstract class EventResponse {
    abstract build();
}

export class Notify extends EventResponse {
    message: string;

    constructor(message: string) {
        super();
        this.message = message;
    }

    build() {
        return { renderActions: { action: { notification: { text: this.message } } } };
    }
}

export class PushCard extends EventResponse {
    card: Card;

    constructor(card: Card) {
        super();
        this.card = card;
    }

    build() {
        return { action: { navigations: [{ pushCard: this.card.build() }] } };
    }
}
export class PushToRoot extends EventResponse {
    card: Card;

    constructor(card: Card) {
        super();
        this.card = card;
    }

    build() {
        return { action: { navigations: [{ popToRoot: true }, { pushCard: this.card.build() }] } };
    }
}

export class PopCard extends EventResponse {
    build() {
        return { action: { navigations: [{ pop: true }] } };
    }
}

export class PopOneCardAndUpdate extends EventResponse {
    card: Card;

    constructor(card: Card) {
        super();
        this.card = card;
    }

    build() {
        return { action: { navigations: [{ pop: true }, { updateCard: this.card.build() }] } };
    }
}

export class UpdateCard extends EventResponse {
    card: Card;

    constructor(card: Card) {
        super();
        this.card = card;
    }

    build() {
        return { action: { navigations: [{ updateCard: this.card.build() }] } };
    }
}

export class Redirect extends EventResponse {
    openLink: OpenLink;
    constructor(openLink: OpenLink) {
        super();
        this.openLink = openLink;
    }

    build() {
        return { action: { link: this.openLink.build()["openLink"] } };
    }
}

/**
 * Create an action which will call the given function and pass the state in arguments.
 */
export class ActionCall {
    state?: State;
    funct: any;
    parameters: any;

    constructor(state: State, funct: Function, parameters: any = {}) {
        if (!eventHandlers[funct.name]) {
            throw new Error(`Event handler not configured: ${funct.name}`);
        }
        this.state = state;
        this.funct = funct;
        this.parameters = parameters;
    }

    build() {
        const payload = {
            state: this.state,
            arguments: this.parameters,
            functionName: this.funct.name,
        };
        const token = jwt.sign(payload, process.env.APP_SECRET, {
            algorithm: "HS256",
            expiresIn: "48h",
        });

        return {
            action: {
                function: HOST + "/execute_action",
                parameters: [
                    {
                        key: "token",
                        value: token,
                    },
                ],
            },
        };
    }
}

/**
 * Define how the event handlers should be declared.
 */
type EventHandler = (
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
) => EventResponse | Promise<EventResponse>;

const eventHandlers = {};
/**
 * Register the function to be able to call it from its name.
 */
export function registerEventHandler(funct: EventHandler) {
    if (!/^on[A-Z][a-zA-Z0-9]+$/.test(funct.name) || eventHandlers.hasOwnProperty(funct.name)) {
        throw new Error(`Invalid function name: ${funct.name}`);
    }
    eventHandlers[funct.name] = funct;
}

/**
 * Get the event handler by the name of the function
 * (everything is serialized when the addin call the event).
 */
export function getEventHandler(functionName: string): EventHandler {
    if (
        !/^on[A-Z][a-zA-Z0-9]+$/.test(functionName) ||
        !eventHandlers.hasOwnProperty(functionName)
    ) {
        throw new Error(`Invalid function name: ${functionName}`);
    }
    return eventHandlers[functionName];
}

export enum OpenLinkOpenAs {
    FULL_SIZE = "FULL_SIZE",
    OVERLAY = "OVERLAY",
}

export class OpenLink {
    url: string;
    openAs: OpenLinkOpenAs;
    reloadOnClose: boolean;

    constructor(
        url: string,
        openAs: OpenLinkOpenAs = OpenLinkOpenAs.FULL_SIZE,
        reloadOnClose: boolean = false,
    ) {
        this.url = url;
        this.openAs = openAs;
        this.reloadOnClose = reloadOnClose;
    }

    build() {
        return {
            openLink: {
                url: this.url,
                openAs: this.openAs,
                onClose: this.reloadOnClose ? "RELOAD" : "NOTHING",
            },
        };
    }
}
