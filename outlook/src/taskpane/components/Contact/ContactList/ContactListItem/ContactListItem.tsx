import * as React from "react";
import {ProfileCard, ProfileCardProps} from "../../../ProfileCard/ProfileCard";
import AppContext from '../../../AppContext';
import Partner from "../../../../../classes/Partner";
import './ContactListItem.css';
import Logger from "../../../Log/Logger";
import { _t } from "../../../../../utils/Translator";

type CustomContactListItemProps = {
    partner: Partner;
    onItemClick?: (partner: Partner) => void;
    selectable:boolean;
};


class ContactListItem extends React.Component<CustomContactListItemProps, {} > {

    constructor(props, context) {
        super(props, context);
        this.state = {};
    }


    private onPartnerClick = () => {
      this.props.onItemClick(this.props.partner);
    };

    render() {
        const profileCardData = {
            domain: undefined,
            name: this.props.partner.name,
            email: this.props.partner.email,
            icon: this.props.partner.image ? "data:image;base64, " + this.props.partner.image : undefined,
            initials: this.props.partner.getInitials(),
            job: this.props.partner.title,
            phone: this.props.partner.phone,
            description: undefined,
            twitter: undefined,
            facebook: undefined,
            crunchbase: undefined,
            linkedin: undefined,
            isBig: !this.context.isConnected() || (!this.props.partner.isAddedToDatabase())
        } as ProfileCardProps;

        let addButton = null;
        let logButton = null;

        if (this.props.partner.isAddedToDatabase())
        {
            logButton = (<Logger resId={this.props.partner.id} model="res.partner" tooltipContent={_t("Log Email Into Contact")}/>);
        }

        let classNames = "contact-list-item-container";
        if (this.props.selectable)
            classNames+= " contact-list-item-container-selectable";

        return <React.Fragment>
            <div onClick={this.onPartnerClick} className={classNames}>
                {addButton}
                <div className='contact-profile-card-container'>
                    <ProfileCard {...profileCardData} />
                </div>
                {logButton}
            </div>
        </React.Fragment>;
    }

}
ContactListItem.contextType = AppContext;
export default ContactListItem;
