import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/api/auth/login', {
        email,
        password,
      });

      // Lưu token
      localStorage.setItem('token', response.data.token);
      
      // Chuyển hướng
      // (Vì đây là demo nên chuyển hướng về trang home.html gốc của template)
      window.location.href = '../../template/home.html';
    } catch (err) {
      setError(err.response?.data?.error || 'Đã có lỗi xảy ra khi đăng nhập.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="absolute top-[-20%] left-[-10%] w-[60vw] h-[60vw] bg-primary-container rounded-full blur-[120px] opacity-20 pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-20%] w-[50vw] h-[50vw] bg-secondary-container/10 rounded-full blur-[100px] opacity-30 pointer-events-none"></div>
      
      <main className="w-full max-w-[420px] px-margin-mobile z-10 flex flex-col">
        {/* Header / Identity */}
        <div className="flex flex-col mb-xl">
          <div className="w-16 h-16 rounded-xl bg-surface-container-lowest border border-outline-variant/30 flex items-center justify-center shadow-[0_4px_30px_rgba(0,0,0,0.05)] mb-md">
            <span className="material-symbols-outlined text-secondary text-[32px]" style={{fontVariationSettings: '"FILL" 1'}}>menu_book</span>
          </div>
          <h1 className="font-display-lg text-display-lg text-on-surface">Chào mừng<br/><span className="text-secondary">trở lại</span></h1>
        </div>
        
        {/* Form Section */}
        <form className="flex flex-col gap-md w-full" onSubmit={handleLogin}>
          {error && <div className="text-error bg-error-container p-3 rounded-lg text-sm">{error}</div>}
          
          {/* Email Input */}
          <div className="flex flex-col gap-xs group">
            <label className="font-label-lg text-label-lg text-on-surface-variant uppercase ml-1" htmlFor="email">Email</label>
            <div className="relative flex items-center">
              <span className="material-symbols-outlined absolute left-4 text-outline group-focus-within:text-secondary transition-colors">mail</span>
              <input
                className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg py-4 pl-12 pr-4 font-body-md text-on-surface placeholder:text-outline focus:outline-none focus:border-secondary focus:ring-1 focus:ring-secondary transition-all"
                id="email" placeholder="email@example.com" type="email"
                value={email} onChange={(e) => setEmail(e.target.value)} required
              />
            </div>
          </div>
          
          {/* Password Input */}
          <div className="flex flex-col gap-xs group">
            <label className="font-label-lg text-label-lg text-on-surface-variant uppercase ml-1" htmlFor="password">Mật khẩu</label>
            <div className="relative flex items-center">
              <span className="material-symbols-outlined absolute left-4 text-outline group-focus-within:text-secondary transition-colors">lock</span>
              <input
                className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg py-4 pl-12 pr-12 font-body-md text-on-surface placeholder:text-outline focus:outline-none focus:border-secondary focus:ring-1 focus:ring-secondary transition-all"
                id="password" placeholder="••••••••" type="password"
                value={password} onChange={(e) => setPassword(e.target.value)} required
              />
              <button className="absolute right-4 text-outline hover:text-on-surface transition-colors focus:outline-none" type="button">
                <span className="material-symbols-outlined">visibility_off</span>
              </button>
            </div>
          </div>
          
          {/* Actions Row */}
          <div className="flex justify-end mt-[-8px]">
            <a className="font-label-lg text-label-lg text-primary hover:text-primary-container transition-colors" href="#">Quên mật khẩu?</a>
          </div>
          
          {/* Submit Button */}
          <button
            className="w-full bg-primary-container text-white font-label-lg text-label-lg uppercase tracking-wider py-4 rounded-full mt-sm hover:bg-primary transition-colors shadow-[0_4px_20px_rgba(255,107,0,0.25)] active:scale-[0.98]"
            type="submit" disabled={loading}>
            {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
          </button>
        </form>
        
        {/* Divider */}
        <div className="flex items-center gap-4 my-lg">
          <div className="flex-1 h-[1px] bg-outline-variant/50"></div>
          <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider text-[11px]">Hoặc tiếp tục với</span>
          <div className="flex-1 h-[1px] bg-outline-variant/50"></div>
        </div>
        
        {/* Social Login */}
        <div className="grid grid-cols-2 gap-sm">
          <button className="flex items-center justify-center gap-base py-3 border border-outline-variant rounded-lg bg-surface-container-lowest hover:bg-surface-container-low transition-colors group" type="button">
            <span className="material-symbols-outlined text-[20px] text-on-surface group-hover:text-primary transition-colors">language</span>
            <span className="font-label-lg text-label-lg text-on-surface">Google</span>
          </button>
          <button className="flex items-center justify-center gap-base py-3 border border-outline-variant rounded-lg bg-surface-container-lowest hover:bg-surface-container-low transition-colors group" type="button">
            <span className="material-symbols-outlined text-[20px] text-on-surface group-hover:text-primary transition-colors">smartphone</span>
            <span className="font-label-lg text-label-lg text-on-surface">Apple</span>
          </button>
        </div>
        
        {/* Sign Up Link */}
        <div className="text-center mt-xl">
          <p className="font-body-md text-body-md text-on-surface-variant">
            Chưa có tài khoản?
            <Link className="font-label-lg text-label-lg text-secondary hover:text-secondary-container transition-colors ml-1" to="/signup">Đăng ký ngay</Link>
          </p>
        </div>
      </main>
    </>
  );
};

export default Login;
