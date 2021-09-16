import * as React from 'react';
import './ProfileCard.css';
import { faEnvelope, faPhone } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { TooltipHost, TooltipOverflowMode } from 'office-ui-fabric-react';
import AppContext from '../AppContext';

const defaultCompanyImageSrc = 'assets/company_image.png';

export type ProfileCardProps = {
    domain: string;
    icon: string;
    initials: string;
    name: string;
    email: string;
    job: string;
    phone: string;
    onClick?: () => void;
    isBig?: boolean; //used for email overflow, TODO change maybe by obtaining the width dynamically
    isCompany: boolean;
};

export class ProfileCard extends React.Component<ProfileCardProps, {}> {
    constructor(props, context) {
        super(props, context);
        this.state = {};
    }

    private getIconOrInitials = () => {
        let iconOrInitials = <img className="icon" src={this.props.icon} />;

        if (!this.props.icon) {
            if (this.props.isCompany) {
                iconOrInitials = <img className="icon" src={defaultCompanyImageSrc} />;
            } else {
                iconOrInitials = <div data-initials={this.props.initials}></div>;
            }
        } else {
            if (this.props.domain) {
                iconOrInitials = (
                    <a href={this.props.domain} target="_blank" rel="noreferrer noopener">
                        {iconOrInitials}
                    </a>
                );
            }
        }

        return iconOrInitials;
    };

    render() {
        const { name, email, job, phone } = this.props;

        //TODO, can we calculate width dynamically?
        let maxEmailWidth = this.props.isBig ? 180 : 120;

        let emailDiv = null;
        if (email) {
            emailDiv = (
                <div className="profile-card-email" style={{ display: 'flex', flexDirection: 'row' }}>
                    <div>
                        <FontAwesomeIcon
                            style={{ marginRight: '4px' }}
                            icon={faEnvelope}
                            color="darkgrey"
                            className="fa-fw"
                        />
                    </div>
                    <div
                        style={{
                            overflow: 'hidden',
                            whiteSpace: 'nowrap',
                            textOverflow: 'ellipsis',
                            maxWidth: maxEmailWidth + 'px',
                        }}>
                        <TooltipHost content={email} overflowMode={TooltipOverflowMode.Parent}>
                            {email}
                        </TooltipHost>
                    </div>
                </div>
            );
        }

        let phoneDiv = null;
        if (phone) {
            phoneDiv = (
                <div className="phone">
                    <div>
                        <FontAwesomeIcon
                            style={{ marginRight: '4px' }}
                            icon={faPhone}
                            color="darkgrey"
                            className="fa-fw"
                        />
                    </div>
                    <div>
                        <a className="link-like-button" href={`tel:${phone}`}>
                            {phone}
                        </a>
                    </div>
                </div>
            );
        }

        return (
            <>
                <div>
                    <div className={`profile-card ${this.props.onClick && 'clickable'}`} onClick={this.props.onClick}>
                        {this.getIconOrInitials()}
                        <div>
                            <div className="name">{job ? name + ', ' + job : name}</div>
                            {emailDiv}
                            {phoneDiv}
                        </div>
                    </div>
                </div>
            </>
        );
    }
}

ProfileCard.contextType = AppContext;
