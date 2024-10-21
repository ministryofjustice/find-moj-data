from typing import cast

from azure_auth.backends import AzureBackend
from azure_auth.handlers import AuthHandler
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, Group

UserModel = cast(AbstractBaseUser, get_user_model())


def user_mapping_fn(**attributes):
    return {
        "first_name": attributes["givenName"],
        "last_name": attributes["surname"],
    }


class MojAzurebackend(AzureBackend):
    def authenticate(self, request, token=None, *args, **kwargs):
        if not token:  # pragma: no cover
            return
        user = MojAuthHandler(request).authenticate(token)

        # Return only if `is_active`
        if self.user_can_authenticate(user):
            return user


class MojAuthHandler(AuthHandler):
    def authenticate(self, token: dict) -> AbstractBaseUser:
        """
        Helper method overrides azure_auth.handlers.AuthHander.authentication.

        We need to make the natural_key (which maps to email in our usermodel) lowercase
        as azure has been changing the casing of user emails and this has prevented users
        from authenticating with the service.

        This method makes the natural key lowercase and is the only difference
        """
        azure_user = self._get_azure_user(token["access_token"])

        # Get extra fields
        extra_fields = {}
        if fields := settings.AZURE_AUTH.get("EXTRA_FIELDS"):  # pragma: no branch
            extra_fields = self._get_azure_user(token["access_token"], fields=fields)

        # Combine user profile attributes, extra attributes and ID token claims
        # https://learn.microsoft.com/en-us/entra/external-id/customers/concept-user-attributes
        # https://learn.microsoft.com/en-us/entra/identity-platform/id-token-claims-reference
        attributes = {**azure_user, **extra_fields, **token.get("id_token_claims", {})}
        natural_key = attributes[settings.AZURE_AUTH["USERNAME_ATTRIBUTE"]].lower()
        try:
            user = UserModel._default_manager.get_by_natural_key(natural_key)  # type: ignore

            # Sync Django user with AAD attributes
            self._update_user(user, **attributes)
        except UserModel.DoesNotExist:
            user = UserModel._default_manager.create_user(  # type: ignore
                **{UserModel.USERNAME_FIELD: natural_key},  # type: ignore
                **self._map_attributes_to_user(**attributes),
            )

        # Syncing azure token claim roles with django user groups
        # A role mapping in the AZURE_AUTH settings is expected.
        role_mappings = settings.AZURE_AUTH.get("ROLES")
        azure_token_roles = token.get("id_token_claims", {}).get("roles", None)
        if role_mappings:  # pragma: no branch
            for role, group_name in role_mappings.items():
                # all groups are created by default if they not exist
                django_group = Group.objects.get_or_create(name=group_name)[0]

                if azure_token_roles and role in azure_token_roles:
                    # Add user with permissions to the corresponding django group
                    user.groups.add(django_group)
                else:
                    # No permission so check if user is in group and remove
                    if user.groups.filter(name=group_name).exists():
                        user.groups.remove(django_group)

        return user
