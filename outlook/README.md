# Odoo for outlook

## To be able to serve the add-in

- cd to the addin-in sources directory
- `npm install`
- `npm run-script build`
- copy the `manifest.xml` to the `dist` directory
- open the `manifest.xml` and replace all `https://localhost:3000` instances with the actual address
- do the same operation with `api.js`
- serve
