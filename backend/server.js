require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

// Initialize SQLite database
const dbPath = path.resolve(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Lỗi khi kết nối với SQLite database:', err.message);
    } else {
        console.log('Đã kết nối với SQLite database.');
        // Tạo bảng users nếu chưa có
        db.run(`CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);
    }
});

const JWT_SECRET = process.env.JWT_SECRET || 'fallback_secret';

// API Đăng ký (Register)
app.post('/api/auth/register', async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(400).json({ error: 'Email và mật khẩu là bắt buộc.' });
    }

    try {
        // Kiểm tra xem email đã tồn tại chưa
        db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, row) => {
            if (err) return res.status(500).json({ error: 'Lỗi database.' });
            if (row) return res.status(400).json({ error: 'Email đã được đăng ký.' });

            // Băm mật khẩu để bảo mật
            const salt = await bcrypt.genSalt(10);
            const hashedPassword = await bcrypt.hash(password, salt);

            // Lưu người dùng vào database
            db.run(`INSERT INTO users (email, password) VALUES (?, ?)`, [email, hashedPassword], function(err) {
                if (err) return res.status(500).json({ error: 'Lỗi khi tạo người dùng.' });
                
                res.status(201).json({ message: 'Đăng ký thành công.', userId: this.lastID });
            });
        });
    } catch (error) {
        res.status(500).json({ error: 'Lỗi server.' });
    }
});

// API Đăng nhập (Login)
app.post('/api/auth/login', async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(400).json({ error: 'Email và mật khẩu là bắt buộc.' });
    }

    try {
        // Tìm người dùng trong database
        db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
            if (err) return res.status(500).json({ error: 'Lỗi database.' });
            if (!user) return res.status(401).json({ error: 'Email hoặc mật khẩu không đúng.' });

            // So sánh mật khẩu đã băm
            const isMatch = await bcrypt.compare(password, user.password);
            if (!isMatch) return res.status(401).json({ error: 'Email hoặc mật khẩu không đúng.' });

            // Tạo JWT token (hết hạn sau 1 ngày)
            const token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET, { expiresIn: '1d' });

            res.json({
                message: 'Đăng nhập thành công.',
                token,
                user: { id: user.id, email: user.email }
            });
        });
    } catch (error) {
        res.status(500).json({ error: 'Lỗi server.' });
    }
});

// Middleware xác thực JWT cho các route cần bảo vệ
const verifyToken = (req, res, next) => {
    const token = req.headers['authorization']?.split(' ')[1]; // Format: Bearer <token>
    
    if (!token) return res.status(403).json({ error: 'Không tìm thấy token. Yêu cầu đăng nhập.' });

    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        req.user = decoded;
        next();
    } catch (err) {
        return res.status(401).json({ error: 'Token không hợp lệ hoặc đã hết hạn.' });
    }
};

// API Protected Route (Ví dụ)
app.get('/api/auth/me', verifyToken, (req, res) => {
    res.json({ message: 'Thông tin xác thực hợp lệ.', user: req.user });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server đang chạy tại http://localhost:${PORT}`);
});
