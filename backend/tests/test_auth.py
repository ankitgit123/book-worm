"""Tests for /auth endpoints."""

import pytest
from tests.conftest import auth_headers, make_user


class TestRegister:
    def test_register_success(self, client):
        resp = client.post(
            "/auth/register",
            json={
                "name": "Alice",
                "email": "alice@example.com",
                "password": "secret123",
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "alice@example.com"
        assert body["name"] == "Alice"
        assert body["gift_points_balance"] == 0
        assert "id" in body

    def test_register_email_normalised_to_lowercase(self, client):
        resp = client.post(
            "/auth/register",
            json={
                "name": "Bob",
                "email": "BOB@EXAMPLE.COM",
                "password": "secret123",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["email"] == "bob@example.com"

    def test_register_duplicate_email(self, client):
        payload = {
            "name": "Alice",
            "email": "alice@example.com",
            "password": "secret123",
        }
        client.post("/auth/register", json=payload)
        resp = client.post("/auth/register", json=payload)
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_register_short_name_rejected(self, client):
        resp = client.post(
            "/auth/register",
            json={"name": "A", "email": "a@b.com", "password": "secret123"},
        )
        assert resp.status_code == 422

    def test_register_short_password_rejected(self, client):
        resp = client.post(
            "/auth/register",
            json={"name": "Alice", "email": "alice@example.com", "password": "abc"},
        )
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client, db):
        make_user(db, email="carol@example.com", password="pass1234")
        resp = client.post(
            "/auth/login",
            json={"email": "carol@example.com", "password": "pass1234"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_login_wrong_password(self, client, db):
        make_user(db, email="dave@example.com", password="correct")
        resp = client.post(
            "/auth/login",
            json={"email": "dave@example.com", "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_login_unknown_email(self, client):
        resp = client.post(
            "/auth/login",
            json={"email": "nobody@example.com", "password": "anything"},
        )
        assert resp.status_code == 401

    def test_login_email_case_insensitive(self, client, db):
        make_user(db, email="eve@example.com", password="pass1234")
        resp = client.post(
            "/auth/login",
            json={"email": "EVE@EXAMPLE.COM", "password": "pass1234"},
        )
        assert resp.status_code == 200


class TestGetMe:
    def test_get_me_authenticated(self, client, db):
        make_user(db, email="frank@example.com", password="pass1234")
        headers = auth_headers(
            client, email="frank@example.com", password="pass1234"
        )
        resp = client.get("/auth/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "frank@example.com"

    def test_get_me_unauthenticated(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_get_me_invalid_token(self, client):
        resp = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer totally.invalid.token"},
        )
        assert resp.status_code == 401
