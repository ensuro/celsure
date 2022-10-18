import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from policies.models import Brand, Model, Policy


def create_phones():
    # Create brand
    brand = Brand.objects.create(code="Brand-0", name="Phone Brand")
    brand.save()

    # Create model
    model = Model.objects.create(brand=brand, name="Testing1", code="Phone Brand-Testing1", fix_price=100)
    model.save()


def test_not_logged_in_redirect_to_login(client):
    # Cant see policy_list if not logged in
    resp = client.get("", follow=True)
    assertRedirects(resp, "/accounts/login/?next=/")
    assertTemplateUsed(resp, "registration/login.html")


@pytest.mark.django_db
def test_login_and_render_policy_list(client, django_user_model):
    # Cant see policy_list if not logged in
    response = client.get("", follow=True)
    assertTemplateUsed(response, "registration/login.html")

    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    response = client.get("", follow=True)
    assertTemplateUsed(response, "policies/policy_list.html")


def test_create_new_policy_form(client, django_user_model):
    # Login
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    url = reverse("new_policy")
    response = client.get(url, follow=True)

    assert response.status_code == 200
    assertTemplateUsed(response, "policies/new_policy.html")

    create_phones()
    model = Model.objects.get(name="Testing1")
    url = reverse("new_policy")

    # form = PolicyForm(
    #     data={
    #         "model": model.code,
    #         "phone_color": "#000000",
    #         "imei": "356938035643809",
    #         "phone_number": "+541112345678",
    #     }
    # )
    data = {
        "model": model.code,
        "phone_color": "#000000",
        "imei": "356938035643809",
        "phone_number": "+541112345678",
    }
    # assert form.is_valid()

    response = client.post(url, data, follow=True)
    assert response.status_code == 200
    assertTemplateUsed(response, "feedback/policy_created.html")
    assert Policy.objects.count() == 1
