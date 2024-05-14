cd app

cp -a node_modules/govuk-frontend/dist/govuk/assets/. static/assets \
    && cp -a node_modules/@ministryofjustice/frontend/moj/assets/images/. static/assets/images

cp node_modules/govuk-frontend/dist/govuk/govuk-frontend.min.js static/assets/js/govuk-frontend.min.js \
    && cp node_modules/govuk-frontend/dist/govuk/govuk-frontend.min.js.map static/assets/js/govuk-frontend.min.js.map \
    && cp node_modules/@ministryofjustice/frontend/moj/all.jquery.min.js static/assets/js/moj-frontend.min.js

sass --load-path=. scss:static/assets/css
