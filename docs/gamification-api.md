# API Gamification – Nhiệm vụ, Timer, Chuỗi ngày

Tất cả endpoint yêu cầu JWT (cookie đăng nhập).

## Khảo sát (`UserProfile`)

| Method | Path | Body |
|--------|------|------|
| GET | `/api/user/profile` | — |
| PUT | `/api/user/profile` | `{ "age", "interests", "mood" }` |

Dùng từ `index.html`; dữ liệu được đưa vào prompt AI tại `home.html`.

## Nhiệm vụ

| Method | Path | Mô tả |
|--------|------|--------|
| GET | `/api/user/missions` | 10 nhiệm vụ, 3 thử thách, 6 danh hiệu + tiến độ |
| POST | `/api/user/missions/<id>/activate` | Chọn nhiệm vụ cho Focus Timer |
| POST | `/api/user/missions/<id>/progress` | Cập nhật tiến độ (nhiệm vụ không dùng timer) |

Catalog seed: `backend/seed_data.py` (chạy khi khởi động app).

## Focus Timer

| Method | Path | Mô tả |
|--------|------|--------|
| GET | `/api/user/timer/active` | Nhiệm vụ đang chọn |
| POST | `/api/user/timer/complete` | `{ "minutes" }` – hoàn thành nếu đủ phút yêu cầu |

`timer.html`: nếu chưa activate → thông báo quay lại Khám phá.

## Chuỗi ngày

| Method | Path | Query |
|--------|------|-------|
| GET | `/api/user/streak` | `year`, `month` |
| GET | `/api/user/stats` | — |

Ghi nhận ngày đọc qua `ReadingDay` khi hoàn thành timer.
