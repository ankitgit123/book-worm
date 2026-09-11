"""Tests for /addresses endpoints."""

from tests.conftest import auth_headers, make_user


def _address_payload(**overrides) -> dict:
    base = {
        "full_name": "John Doe",
        "address_line1": "123 Main St",
        "address_line2": None,
        "city": "Springfield",
        "state": "IL",
        "postal_code": "62701",
        "country": "US",
        "is_default": False,
    }
    base.update(overrides)
    return base


class TestCreateAddress:
    def test_create_address_authenticated(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post("/addresses", json=_address_payload(), headers=headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["full_name"] == "John Doe"
        assert body["city"] == "Springfield"
        assert body["is_default"] is False

    def test_create_address_unauthenticated(self, client):
        resp = client.post("/addresses", json=_address_payload())
        assert resp.status_code == 401

    def test_create_default_address_unsets_others(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        first = client.post(
            "/addresses", json=_address_payload(is_default=True), headers=headers
        )
        assert first.json()["is_default"] is True
        second = client.post(
            "/addresses",
            json=_address_payload(full_name="Jane Doe", is_default=True),
            headers=headers,
        )
        assert second.json()["is_default"] is True
        # The first address is no longer default
        first_id = first.json()["id"]
        resp = client.get(f"/addresses/{first_id}", headers=headers)
        assert resp.json()["is_default"] is False


class TestGetAddresses:
    def test_get_addresses_empty(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.get("/addresses", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_addresses_returns_own_only(self, client, db):
        make_user(db, email="user1@example.com", password="pass1234")
        make_user(db, email="user2@example.com", password="pass1234")
        h1 = auth_headers(client, email="user1@example.com", password="pass1234")
        h2 = auth_headers(client, email="user2@example.com", password="pass1234")
        client.post("/addresses", json=_address_payload(), headers=h1)
        resp = client.get("/addresses", headers=h2)
        assert resp.json() == []

    def test_get_address_unauthenticated(self, client):
        resp = client.get("/addresses")
        assert resp.status_code == 401


class TestGetAddressById:
    def test_get_address_by_id(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        created = client.post("/addresses", json=_address_payload(), headers=headers)
        addr_id = created.json()["id"]
        resp = client.get(f"/addresses/{addr_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == addr_id

    def test_get_address_not_found(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.get("/addresses/99999", headers=headers)
        assert resp.status_code == 404

    def test_cannot_access_another_users_address(self, client, db):
        make_user(db, email="user1@example.com", password="pass1234")
        make_user(db, email="user2@example.com", password="pass1234")
        h1 = auth_headers(client, email="user1@example.com", password="pass1234")
        h2 = auth_headers(client, email="user2@example.com", password="pass1234")
        addr_id = client.post("/addresses", json=_address_payload(), headers=h1).json()["id"]
        resp = client.get(f"/addresses/{addr_id}", headers=h2)
        assert resp.status_code == 404


class TestUpdateAddress:
    def test_update_address(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = client.post(
            "/addresses", json=_address_payload(), headers=headers
        ).json()["id"]
        resp = client.put(
            f"/addresses/{addr_id}",
            json={"city": "Chicago"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["city"] == "Chicago"

    def test_update_address_not_found(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.put("/addresses/99999", json={"city": "X"}, headers=headers)
        assert resp.status_code == 404


class TestSetDefaultAddress:
    def test_set_default_address(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = client.post(
            "/addresses", json=_address_payload(), headers=headers
        ).json()["id"]
        resp = client.post(f"/addresses/{addr_id}/default", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["is_default"] is True

    def test_set_default_unsets_previous(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        first_id = client.post(
            "/addresses", json=_address_payload(is_default=True), headers=headers
        ).json()["id"]
        second_id = client.post(
            "/addresses", json=_address_payload(full_name="Jane"), headers=headers
        ).json()["id"]
        client.post(f"/addresses/{second_id}/default", headers=headers)
        first_resp = client.get(f"/addresses/{first_id}", headers=headers)
        assert first_resp.json()["is_default"] is False


class TestDeleteAddress:
    def test_delete_address(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = client.post(
            "/addresses", json=_address_payload(), headers=headers
        ).json()["id"]
        resp = client.delete(f"/addresses/{addr_id}", headers=headers)
        assert resp.status_code == 200
        assert client.get(f"/addresses/{addr_id}", headers=headers).status_code == 404

    def test_delete_address_not_found(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.delete("/addresses/99999", headers=headers)
        assert resp.status_code == 404
