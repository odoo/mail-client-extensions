import * as React from "react";
import Login from "./Login/Login"
import Main from "./Main/Main";
import AppContext from './AppContext';
import EnrichmentInfo, {EnrichmentInfoType} from "../../classes/EnrichmentInfo";
import {IIconProps, Link, MessageBar, MessageBarType} from "office-ui-fabric-react";
import Progress from "./GrayOverlay";
import { _t } from "../../utils/Translator";

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
    EnrichmentInfo: EnrichmentInfo;
    showPartnerCreatedMessage: boolean;
    showEnrichmentInfoMessage: boolean;
    userCompanies: number[];
    loginErrorMessage: string;
    navigation: {
        goToLogin: () => void,
        goToMain: () => void
        },
    connect: (token) => void,
    disconnect: () => void,
    getConnectionToken: () => void,
    getUserCompaniesString: () => string,
    isConnected: () => Boolean,
    cancelRequests: () => void,
    addRequestCanceller: (canceller: () => void) => void,
    setUserCompanies: (userCompanies: number[]) => void,
    showTopBarMessage: (enrichmentInfo?: EnrichmentInfo) => void,
    showHttpErrorMessage: (error) => void
}

export default class App extends React.Component<AppProps, AppState> {
    requestCancellers: (() => void)[] = [];

    constructor(props, context) {
        super(props, context);

        props.itemChangedRegister(this.itemChanged);

        this.state = {
            EnrichmentInfo: new EnrichmentInfo(),
            showPartnerCreatedMessage: false,
            showEnrichmentInfoMessage: false,
            userCompanies: [],
            pageDisplayed: Page.Main,
            loginErrorMessage: "",
            navigation: {
                goToLogin: this.goToLogin,
                goToMain: this.goToMain
            },
            connect: (token) => {
                localStorage.setItem('odooConnectionToken', token);
            },
            disconnect: () => {
                localStorage.removeItem('odooConnectionToken');
                localStorage.removeItem('translations');
                localStorage.removeItem('translationsTimestamp');
            },
            getConnectionToken: () => {
                return 'Bearer ' + localStorage.getItem('odooConnectionToken');
            },
            getUserCompaniesString: () => {
                if (this.state.userCompanies.length == 0) {
                    return '';
                } else {
                    return `&cids=${this.state.userCompanies.sort().join(',')}`;
                }
            },
            isConnected: () => {
                return !!localStorage.getItem('odooConnectionToken');
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
            },

            setUserCompanies: (companies: number[]) => {
                this.setState({userCompanies: companies});
            },

            showTopBarMessage: (enrichmentInfo) => {
                if (enrichmentInfo)
                    this.setState({
                        EnrichmentInfo: enrichmentInfo,
                        showEnrichmentInfoMessage: true
                    });
                else
                    this.setState({
                        EnrichmentInfo: new EnrichmentInfo(EnrichmentInfoType.ConnectionError),
                        showEnrichmentInfoMessage: true
                    });
            },

            showHttpErrorMessage: (error?) => {
                if (error && error.message == '0')
                {
                    this.setState({
                        EnrichmentInfo: new EnrichmentInfo(EnrichmentInfoType.ConnectionError),
                        showEnrichmentInfoMessage: true
                    });
                }
                else
                {
                    this.setState({
                        EnrichmentInfo: new EnrichmentInfo(EnrichmentInfoType.Other),
                        showEnrichmentInfoMessage: true
                    });
                }
            },

        };
    }

    private getMessageBars = () => {
        const {type, info} = this.state.EnrichmentInfo;
        const message = this.state.EnrichmentInfo.getTypicalMessage();
        const warningIcon: IIconProps = {
            iconName: 'Error',
            style: {fontSize: "20px"},
        };
        let bars = [];
        if (this.state.showPartnerCreatedMessage) {
            bars.push(<MessageBar messageBarType={MessageBarType.success} onDismiss={this.hidePartnerCreatedMessage}>{_t("Contact created")}</MessageBar>);
        }
        if (this.state.showEnrichmentInfoMessage) {
            switch (type) {
                case EnrichmentInfoType.CompanyCreated:
                    bars.push(<MessageBar messageBarType={MessageBarType.success} onDismiss={this.hideEnrichmentInfoMessage}>{_t("Company created")}</MessageBar>);
                    break;
                case EnrichmentInfoType.NoData:
                case EnrichmentInfoType.NotConnected_NoData:
                    bars.push(<MessageBar messageBarType={MessageBarType.info} onDismiss={this.hideEnrichmentInfoMessage}>{message}</MessageBar>);
                    break;
                case EnrichmentInfoType.InsufficientCredit:

                    bars.push(<MessageBar messageBarType={MessageBarType.error} messageBarIconProps={warningIcon}  onDismiss={this.hideEnrichmentInfoMessage}>
                        {message}
                        <br/>
                        <Link href={info} target="_blank">
                            {_t("Buy More")}
                        </Link>
                    </MessageBar>);
                    break;
                case EnrichmentInfoType.EnrichContactWithNoEmail:
                case EnrichmentInfoType.NotConnected_InsufficientCredit:
                case EnrichmentInfoType.NotConnected_InternalError:
                case EnrichmentInfoType.Other:
                case EnrichmentInfoType.CouldNotGetTranslations:
                case EnrichmentInfoType.ConnectionError:
                    bars.push(<MessageBar messageBarType={MessageBarType.error} messageBarIconProps={warningIcon} onDismiss={this.hideEnrichmentInfoMessage}>{message}</MessageBar>);
                    break;
            }
        }
        return bars;
    }

    private goToLogin = () => {
        this.setState({
        pageDisplayed: Page.Login
        })
    }

    private goToMain = () => {
        this.setState({
        pageDisplayed: Page.Main
        })
    }

    private itemChanged = () => {

    }

    private hideEnrichmentInfoMessage = () => {
        this.setState({
            showEnrichmentInfoMessage: false
        })
    }

    private hidePartnerCreatedMessage = () => {
        this.setState({
            showPartnerCreatedMessage: false
        })
    }

    render() {
        const { isOfficeInitialized } = this.props;

        if (!isOfficeInitialized) {
            return (
                <Progress />
            );
        }

        switch (this.state.pageDisplayed) {
        case Page.Login:
            return <AppContext.Provider value={this.state}><Login /></AppContext.Provider>
        case Page.Main:
        default:

            return (
                <AppContext.Provider value={this.state}>
                    <div style={{height: "100vh", width:"100hw", display: "flex", flexDirection: "column"}}>
                        <div>
                            {this.getMessageBars()}
                        </div>
                        <div style={{flex: 1}}>
                            <Main />
                        </div>
                    </div>
                </AppContext.Provider>
            );
        }
    }
}
