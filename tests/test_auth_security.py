import json

VALID_PASSWORD = "MatKhau123"
VALID_USER = {
    "full_name": "Nguyen Van A",
    "email": "secure.user@example.com",
    "password": VALID_PASSWORD,
    "confirm_password": VALID_PASSWORD,
}


def _post(client, path, payload):
    return client.post(
        path,
        data=json.dumps(payload),
        content_type="application/json",
    )


def _register(client, email=None):
    data = {**VALID_USER, "email": email or VALID_USER["email"]}
    return _post(client, "/api/auth/register", data)


def test_weak_password_rejected(client):
    payload = {
        **VALID_USER,
        "password": "weak",
        "confirm_password": "weak",
    }
    response = _post(client, "/api/auth/register", payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_sql_injection_email_does_not_bypass(client):
    payload = {
        **VALID_USER,
        "email": "' OR '1'='1'--@x.com",
        "password": VALID_PASSWORD,
        "confirm_password": VALID_PASSWORD,
    }
    response = _post(client, "/api/auth/register", payload)
    assert response.status_code in (400, 409)


def test_duplicate_email_returns_409(client):
    first = _register(client)
    assert first.status_code == 201

    second = _register(client)
    assert second.status_code == 409
    assert "đã được sử dụng" in second.get_json()["error"]


def test_login_wrong_password_generic_error(client):
    _register(client)
    response = _post(
        client,
        "/api/auth/login",
        {"email": VALID_USER["email"], "password": "WrongPass1"},
    )
    assert response.status_code == 401
    body = response.get_json()
    assert body["error"] == "Email hoặc mật khẩu không đúng."


def test_login_nonexistent_email_same_error(client):
    response = _post(
        client,
        "/api/auth/login",
        {"email": "nobody@example.com", "password": VALID_PASSWORD},
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "Email hoặc mật khẩu không đúng."


def test_response_never_includes_password_hash(client):
    response = _register(client)
    body = response.get_json()
    dumped = json.dumps(body)
    assert "password_hash" not in dumped
    assert VALID_PASSWORD not in dumped


def test_me_requires_authentication(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_successful_login_sets_httponly_cookie(client):
    _register(client)

    response = _post(
        client,
        "/api/auth/login",
        {"email": VALID_USER["email"], "password": VALID_PASSWORD},
    )
    assert response.status_code == 200

    cookies = response.headers.getlist("Set-Cookie")
    combined = " ".join(cookies)
    assert "HttpOnly" in combined


def test_security_headers_present(client):
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"


def test_password_mismatch_rejected(client):
    payload = {**VALID_USER, "confirm_password": "Khac1234"}
    response = _post(client, "/api/auth/register", payload)
    assert response.status_code == 400
    assert "khớp" in response.get_json()["error"].lower()


def test_authenticated_me_after_register(client):
    reg = _register(client)
    assert reg.status_code == 201

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.get_json()["user"]["email"] == VALID_USER["email"]
