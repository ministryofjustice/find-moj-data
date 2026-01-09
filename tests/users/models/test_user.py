import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user_model = get_user_model()

        params = {
            "email": "user1@example.com",
            "first_name": "Joe",
            "last_name": "Bloggs",
        }
        user = user_model.objects.create(**params)

        assert user.email == params["email"]
        assert user.first_name == params["first_name"]
        assert user.last_name == params["last_name"]

    def test_create_and_retrieve_user(self):
        user_model = get_user_model()

        params = {
            "email": "user1@example.com",
            "first_name": "Joe",
            "last_name": "Bloggs",
        }
        user_model.objects.create(**params)

        user = user_model.objects.get(email=params["email"])

        assert user.email == params["email"]
        assert user.first_name == params["first_name"]
        assert user.last_name == params["last_name"]

    def test_update_user(self):
        user_model = get_user_model()

        params = {
            "email": "user1@example.com",
            "first_name": "Joe",
            "last_name": "Bloggs",
        }
        user = user_model.objects.create(**params)
        user.first_name = "David"
        user.last_name = "Smith"
        user.save()

        assert user.first_name == "David"
        assert user.last_name == "Smith"

    def test_delete_user(self):
        user_model = get_user_model()

        params = {
            "email": "user1@example.com",
            "first_name": "Joe",
            "last_name": "Bloggs",
        }
        user = user_model.objects.create(**params)
        user.delete()

        with pytest.raises(user_model.DoesNotExist) as exc:
            user_model.objects.get(email=params["email"])

        assert "CustomUser matching query does not exist" in str(exc.value)

    def test_duplicate_email(self):
        user_model = get_user_model()

        params = {
            "email": "user1@example.com",
            "first_name": "Joe",
            "last_name": "Bloggs",
        }
        user_model.objects.create(**params)

        with pytest.raises(IntegrityError) as exc:
            user_model.objects.create(**params)

        assert "UNIQUE constraint failed: users_customuser.email" in str(exc.value)
