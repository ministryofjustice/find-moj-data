# Django Development Variables
DEBUG=op://Data-Catalogue/Find-Moj-Data/${ENV}/Django-Debug
SECRET_KEY=op://Data-Catalogue/Find-Moj-Data/${ENV}/Django-Secret-Key # pragma: allowlist secret
DJANGO_ALLOWED_HOSTS=op://Data-Catalogue/Find-Moj-Data/${ENV}/Django-Allowed-Hosts
DJANGO_LOG_LEVEL=op://Data-Catalogue/Find-Moj-Data/${ENV}/Django-Log-Level

# Catalogue Variables
CATALOGUE_TOKEN=op://Data-Catalogue/Find-Moj-Data/${ENV}/Catalogue-Token
CATALOGUE_URL=op://Data-Catalogue/Find-Moj-Data/${ENV}/Catalogue-Gms-Url

# Azure Variables
# Any value other than 'false' to enable Azure Auth
AZURE_AUTH_ENABLED=op://Data-Catalogue/Find-Moj-Data/${ENV}/Azure-Auth-Enabled
AZURE_CLIENT_ID=op://Data-Catalogue/Find-Moj-Data/${ENV}/Azure-Client-ID
AZURE_CLIENT_SECRET=op://Data-Catalogue/Find-Moj-Data/${ENV}/Azure-Client-Secret # pragma: allowlist secret
AZURE_REDIRECT_URI=op://Data-Catalogue/Find-Moj-Data/${ENV}/Azure-Redirect-Uri
AZURE_AUTHORITY=op://Data-Catalogue/Find-Moj-Data/${ENV}/Azure-Authority

# Sentry Variables
SENTRY_DSN__WORKAROUND=op://Data-Catalogue/Find-Moj-Data/${ENV}/Sentry-Dsn

# Notify API Service
NOTIFY_ENABLED=op://Data-Catalogue/Find-Moj-Data/${ENV}/notify-enabled
NOTIFY_API_KEY=op://Data-Catalogue/Find-Moj-Data/${ENV}/notify-api-key #pragma: allowlist secret
NOTIFY_DATA_OWNER_TEMPLATE_ID=op://Data-Catalogue/Find-Moj-Data/${ENV}/notify-data-owner-template-id
NOTIFY_FEEDBACK_TEMPLATE_ID=op://Data-Catalogue/Find-Moj-Data/${ENV}/notify-feedback-template-id
NOTIFY_SENDER_TEMPLATE_ID=op://Data-Catalogue/Find-Moj-Data/${ENV}/notify-sender-template-id
NOTIFY_DATA_CATALOGUE_TEMPLATE_ID=op://Data-Catalogue/Find-Moj-Data/${ENV}/notify-data-catalogue-template-id

# Data Catalogue Email
DATA_CATALOGUE_EMAIL=op://Data-Catalogue/Find-Moj-Data/${ENV}/data-catalogue-email
