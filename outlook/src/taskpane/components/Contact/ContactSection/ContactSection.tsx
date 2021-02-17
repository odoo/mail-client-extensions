import * as React from "react";
import Partner from "../../../../classes/Partner";

import ContactListItem from "../ContactList/ContactListItem/ContactListItem";

import api from "../../../api";


type ContactSectionProps = {
    partner: Partner;
    onPartnerInfoChanged?: (partner: Partner) => void;
};


const ContactSection = (props: ContactSectionProps) => {

    const viewContact = (partner) => {
        let url = api.baseURL+`/web#id=${partner.id}&model=res.partner&view_type=form`;
        window.open(url,"_blank");
    }

    let selectable = props.partner.isAddedToDatabase();
    let onItemClick = props.partner.isAddedToDatabase() ? viewContact : undefined;

    return (
        <div className='section-card'>
            <ContactListItem partner={props.partner} selectable={selectable}
                             onItemClick={onItemClick}/>
        </div>
    )

}

export default ContactSection;
