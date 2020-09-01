class Address {
    number: string;
    street: string;
    city: string;
    zip: string;
    country: string;

    constructor() {
        this.number = '';
        this.street = '';
        this.city = '';
        this.zip = '';
        this.country = '';
    }

    getLines(): string[] {
        let firstLine = [this.number || "", this.street || ""].join(" ").trim();
        let secondLine = [this.city || "", this.zip || ""].join(" ").trim();

        let lines = [];
        if (firstLine)
            lines.push(firstLine)
        if (secondLine)
            lines.push(secondLine)
        if (this.country)
            lines.push(this.country)

        return lines;
    }

    static fromJSON(o: Object): Address {
        if (!o) return new Address();
        const address = Object.assign(new Address(), o);
        return address;
    }

    static fromRevealJSON(o: Object): Address {
        // TODO see about the "location" field, and "sub_premise".
        // TODO state?
        const address = new Address();
        address.number = o['street_number'];
        address.street = o['street_name'];
        address.city = o['city']
        address.zip = o['postal_code'];
        address.country = o['country_name'];
        return address;
    }
}

export default Address;