# API Xác thực

Base URL (local): `http://127.0.0.1:5000`

Tất cả request JSON dùng header `Content-Type: application/json`.  
Cookie JWT được gửi tự động khi `credentials: include` (trình duyệt).

## POST `/api/auth/register`

Tạo tài khoản mới.

**Body:**

```json
{
  "full_name": "Nguyễn Văn A",
  "email": "user@example.com",
  "password": "MatKhau123",
  "confirm_password": "MatKhau123"
}
```

**Thành công (201):**

```json
{
  "message": "Đăng ký thành công.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Nguyễn Văn A",
    "created_at": "2026-05-16T12:00:00+00:00"
  }
}
```

Set cookie `access_token_cookie`, `refresh_token_cookie` (HttpOnly).

**Lỗi thường gặp:**

| Mã | Nguyên nhân |
|----|-------------|
| 400 | Email/mật khẩu/họ tên không hợp lệ, mật khẩu xác nhận không khớp |
| 409 | Email đã tồn tại |
| 429 | Vượt giới hạn tần suất (`RATELIMIT_AUTH`) |

---

## POST `/api/auth/login`

**Body:**

```json
{
  "email": "user@example.com",
  "password": "MatKhau123"
}
```

**Thành công (200):** Cấu trúc tương tự register (không có 201).

**Lỗi (401):** `{"error": "Email hoặc mật khẩu không đúng."}` — thông báo chung, không tiết lộ email có tồn tại hay không.

---

## GET `/api/auth/me`

Yêu cầu đã đăng nhập (cookie access token hợp lệ).

**Thành công (200):**

```json
{
  "user": { "id": 1, "email": "...", "full_name": "...", "created_at": "..." }
}
```

---

## POST `/api/auth/logout`

Yêu cầu JWT. Xóa cookie phiên.

---

## GET `/api/auth/csrf`

Khởi tạo cookie CSRF (dùng khi gọi API có bảo vệ CSRF sau khi đã có token).

## Quy tắc mật khẩu

- Tối thiểu 8 ký tự (cấu hình `PASSWORD_MIN_LENGTH`)
- Ít nhất 1 chữ hoa, 1 chữ thường, 1 chữ số
- Tối đa 128 ký tự

## Giao diện

Form `login.html` và `signup.html` gọi API qua `static/js/auth.js`. Sau thành công chuyển tới `home.html`.
