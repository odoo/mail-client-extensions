# Odoo for outlook

## To be able to serve the add-in

- cd to the addin-in sources directory
- `npm install`
- `npm run-script build  -- --env.DOMAIN=127.0.0.1:8080` (replace `127.0.0.1:8080` with the actual domain)
- serve the dist folder
