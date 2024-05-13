rm -rf static/assets/images \
    && cp -a node_modules/govuk-frontend/dist/govuk/assets/images static/assets/images \
    && cp -a node_modules/@ministryofjustice/frontend/moj/assets/images/. static/assets/images

rm -rf static/assets/fonts \
    && cp -r node_modules/govuk-frontend/dist/govuk/assets/fonts static/assets/fonts

cp node_modules/govuk-frontend/dist/govuk/govuk-frontend.min.js static/assets/js/govuk-frontend.min.js \
    && cp node_modules/govuk-frontend/dist/govuk/govuk-frontend.min.js.map static/assets/js/govuk-frontend.min.js.map \
    && cp node_modules/@ministryofjustice/frontend/moj/all.jquery.min.js static/assets/js/moj-frontend.min.js

sass --load-path=. scss:static/assets/css
