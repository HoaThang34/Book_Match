# Bảo mật Backend

## Các biện pháp đã triển khai

### Mật khẩu

- Băm bằng **bcrypt** (cost `BCRYPT_ROUNDS`, mặc định 12).
- Không lưu hoặc trả về mật khẩu/plaintext trong API hay log.

### Phiên đăng nhập (JWT)

- Token lưu trong **HttpOnly cookie** (giảm rủi ro XSS đọc token).
- `SameSite=Lax` (cấu hình qua `JWT_COOKIE_SAMESITE`).
- Production: bật `JWT_COOKIE_SECURE=true` khi dùng HTTPS.
- Access token ngắn hạn (mặc định 15 phút), refresh token dài hơn (7 ngày).
- CSRF bật khi dùng cookie (`JWT_CSRF_IN_COOKIES`); client gửi header `X-CSRF-TOKEN` khi có cookie CSRF.

### Đầu vào

- Chuẩn hóa email (trim, lowercase).
- Validate email, họ tên, độ mạnh mật khẩu.
- Giới hạn kích thước body (`MAX_CONTENT_LENGTH`).
- Truy vấn DB qua SQLAlchemy (tham số hóa, chống SQL injection).

### Chống lạm dụng

- **Rate limit** trên `/api/auth/login` và `/api/auth/register` (`RATELIMIT_AUTH`, mặc định 10/phút/IP).
- Thông báo lỗi đăng nhập **chung** (không phân biệt “sai email” / “sai mật khẩu”).

### HTTP headers

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security` khi `JWT_COOKIE_SECURE=true`

### Cấu hình bí mật

- `SECRET_KEY`, `JWT_SECRET_KEY` chỉ trong `.env` (không commit).
- File mẫu: `.env.example`.

## Kiểm thử bảo mật

Chạy sau khi cài dependency:

```bash
pytest tests/test_auth_security.py -v
```

Các kịch bản được kiểm tra:

- Mật khẩu yếu bị từ chối
- Payload SQL injection trên email không bypass xác thực
- Đăng ký trùng email → 409
- Đăng nhập sai → 401, thông báo chung
- Response không chứa hash mật khẩu
- `/api/auth/me` yêu cầu đăng nhập
- Header bảo mật trên response

## Khuyến nghị khi triển khai production

1. HTTPS bắt buộc; `JWT_COOKIE_SECURE=true`.
2. Sinh `SECRET_KEY` và `JWT_SECRET_KEY` bằng `secrets.token_hex(32)`.
3. Cân nhắc PostgreSQL thay SQLite khi nhiều người dùng.
4. Lưu rate limit trên Redis (`RATELIMIT_STORAGE_URI`).
5. Bật log giám sát đăng nhập thất bại (không log mật khẩu).
