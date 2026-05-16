# Cấu hình Backend - AI Reader

Tài liệu này mô tả các cơ chế, cấu hình và thông tin backend cho dự án AI Reader.

## 1. Môi trường (Environment)
- Các biến môi trường được lưu trong file `.env`.
- File `.env.example` cung cấp mẫu các biến cần thiết khi triển khai môi trường mới.

## 2. Cơ chế Đăng nhập & Đăng ký
- Sử dụng Node.js (Express) làm server.
- Sử dụng **SQLite** để lưu trữ người dùng (file data: `database.sqlite`).
- Sử dụng **Bcrypt.js** để băm mật khẩu, đảm bảo tính bảo mật khi lưu trữ.
- Cơ chế xác thực sử dụng **JSON Web Token (JWT)**, đảm bảo stateless và dễ dàng phân quyền.

## 3. Các API Endpoints
- `POST /api/auth/register`: Đăng ký tài khoản mới (Yêu cầu `email`, `password`).
- `POST /api/auth/login`: Đăng nhập (Yêu cầu `email`, `password`). Trả về JWT Token.

## 4. Bảo mật
- Tất cả mật khẩu đều được băm (hashing) trước khi lưu.
- JWT secret cần được bảo vệ nghiêm ngặt trong file `.env`.
- Cần có bước test bảo mật (Penetration Test) đối với các endpoint này trong tương lai.
