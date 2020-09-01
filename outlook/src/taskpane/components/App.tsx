import * as React from "react";
import Login from "./Login/Login"
import Progress from "./Progress";
import Main from "./Main/Main";
import AppContext from './AppContext';
import Partner from "../../classes/Partner";

enum Page {
    Login,
    Main,
}

export interface AppProps {
    title: string;
    isOfficeInitialized: boolean;
    itemChangedRegister: any;
}

export interface AppState {
    pageDisplayed: Page;
    isLoading: Boolean;
    doReload: Boolean;
    lastLoaded: number;
    loginErrorMessage: string;
    navigation: {
        goToLogin: () => void,
        goToMain: () => void
        },
    partner: Partner,
    setPartner: (p: Partner, isLoading: Boolean) => void,
    setPartnerId: (id: number) => void,
    modules: string[],
    setModules: (modules: string[]) => void,
    connect: (token) => void,
    disconnect: () => void,
    getConnectionToken: () => void,
    isConnected: () => Boolean,
    setIsLoading: (isLoading: Boolean) => void,
    setDoReload: (doReload: Boolean) => void,
    cancelRequests: () => void,
    addRequestCanceller: (canceller: () => void) => void
}

export default class App extends React.Component<AppProps, AppState> {
    requestCancellers: (() => void)[] = [];

    constructor(props, context) {
        super(props, context);

        props.itemChangedRegister(this.itemChanged);

        this.state = {
            isLoading: false,
            doReload: false,
            lastLoaded: Date.now(),
            pageDisplayed: Page.Main,
            loginErrorMessage: "",
            
            navigation: {
                goToLogin: this.goToLogin,
                goToMain: this.goToMain
            },
            partner: new Partner(),
            setPartner: (p: Partner, isLoading: Boolean) => {
                const partnerCopy = Partner.fromJSON(JSON.parse(JSON.stringify(p)));
                this.setState({partner: partnerCopy, isLoading: isLoading})
            },
            setPartnerId: (id: number) => {
                const partnerCopy = Partner.fromJSON(JSON.parse(JSON.stringify(this.state.partner)));
                partnerCopy.id = id;
                this.setState({partner: partnerCopy})
            },
            modules: [],
            setModules: (modules: string[]) => {
                this.setState({modules: [...modules]});
            },
            connect: (token) => {
                localStorage.setItem('odooConnectionToken', token);
            },
            disconnect: () => {
                this.setState({modules: []});
                localStorage.removeItem('odooConnectionToken');
            },
            getConnectionToken: () => {
                return 'Bearer ' + localStorage.getItem('odooConnectionToken');
            },
            isConnected: () => {
                return !!localStorage.getItem('odooConnectionToken');
            },
            setIsLoading: (isLoading: Boolean) => {
                this.setState({isLoading: isLoading});
            },
            setDoReload: (doReload: Boolean) => {
                this.setState({
                    doReload: doReload,
                    partner: new Partner(),
                    modules: []
                });
            },
            cancelRequests: () => {
                const cancellers = [...this.requestCancellers];
                this.requestCancellers = [];
                for (const canceller of cancellers){
                    canceller(); // Cancel the request.
                }
            },
            addRequestCanceller: (canceller: () => void) => {
                this.requestCancellers.push(canceller);
            }
        };
    }

    componentDidMount() {
        this.setState({
        isLoading: false,
        });
    }

    goToLogin = () => {
        this.setState({
        pageDisplayed: Page.Login
        })
    }

    goToMain = () => {
        this.setState({
        pageDisplayed: Page.Main
        })
    }

    itemChanged = () => {
        this.setState({'doReload': true});
        //this.forceUpdate();;
    }

    render() {
        const { title, isOfficeInitialized } = this.props;

        if (!isOfficeInitialized) {
            return (
                <Progress title={title} message="Loading..." />
            );
        }

        switch (this.state.pageDisplayed) {
        case Page.Login:
            return <AppContext.Provider value={this.state}><Login /></AppContext.Provider>
        case Page.Main:
        default:
            return <AppContext.Provider value={this.state}><Main /></AppContext.Provider>;
        }
    }
}
