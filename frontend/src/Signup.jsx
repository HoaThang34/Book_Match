import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const Signup = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Mật khẩu xác nhận không khớp.');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/api/auth/register', {
        email,
        password,
      });

      // Nếu thành công, có thể tự động đăng nhập hoặc chuyển sang trang đăng nhập
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.error || 'Đã có lỗi xảy ra khi đăng ký.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Background Glow */}
      <div className="fixed top-[-10%] left-[-10%] w-[120%] h-[120%] pointer-events-none z-0" style={{background: 'radial-gradient(circle at 50% 0%, rgba(255, 107, 0, 0.1) 0%, rgba(249, 249, 255, 1) 60%)'}}></div>
      
      {/* Navigation Shell */}
      <nav className="fixed top-0 left-0 right-0 h-16 bg-surface/80 backdrop-blur-md border-b border-outline-variant z-50 px-margin-mobile md:px-margin-desktop flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center">
            <span className="material-symbols-outlined text-white text-[18px]">menu_book</span>
          </div>
          <span className="font-display text-lg font-bold text-on-surface">AI Reader</span>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/login" className="font-label-lg text-primary hover:text-on-primary-container transition-colors">Đăng nhập</Link>
        </div>
      </nav>
      
      {/* Main Content */}
      <main className="w-full max-w-[480px] z-10 px-margin-mobile py-xl flex flex-col gap-lg mt-16">
        <header className="flex flex-col items-center text-center gap-sm">
          <div className="w-16 h-16 rounded-2xl bg-primary-container flex items-center justify-center shadow-lg mb-2">
            <span className="material-symbols-outlined text-[32px] text-white" style={{fontVariationSettings: '"FILL" 1'}}>menu_book</span>
          </div>
          <h1 className="font-headline-lg-mobile text-headline-lg-mobile text-on-surface">Bắt đầu hành trình</h1>
          <p className="font-body-md text-body-md text-on-surface-variant">Tham gia hành trình tri thức với AI Reader.</p>
        </header>

        {/* Sign Up Form */}
        <form className="flex flex-col gap-md w-full bg-surface/80 backdrop-blur-xl p-6 rounded-2xl border border-black/5 shadow-[0_10px_40px_rgba(0,0,0,0.05)]" onSubmit={handleSignup}>
          {error && <div className="text-error bg-error-container p-3 rounded-lg text-sm">{error}</div>}
          
          <div className="flex flex-col gap-xs">
            <label className="font-label-md text-label-md text-on-surface-variant uppercase">Họ và tên</label>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline group-focus-within:text-primary-container transition-colors">person</span>
              <input className="w-full bg-surface-container-lowest border border-outline rounded-xl py-3 pl-12 pr-4 text-on-surface font-body-md text-body-md placeholder:text-outline focus:outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container transition-all" placeholder="Nguyễn Văn A" type="text" value={name} onChange={e => setName(e.target.value)} required />
            </div>
          </div>

          <div className="flex flex-col gap-xs">
            <label className="font-label-md text-label-md text-on-surface-variant uppercase">Địa chỉ Email</label>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline group-focus-within:text-primary-container transition-colors">mail</span>
              <input className="w-full bg-surface-container-lowest border border-outline rounded-xl py-3 pl-12 pr-4 text-on-surface font-body-md text-body-md placeholder:text-outline focus:outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container transition-all" placeholder="email@example.com" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
            </div>
          </div>

          <div className="flex flex-col gap-xs">
            <label className="font-label-md text-label-md text-on-surface-variant uppercase">Mật khẩu của bạn</label>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline group-focus-within:text-primary-container transition-colors">lock</span>
              <input className="w-full bg-surface-container-lowest border border-outline rounded-xl py-3 pl-12 pr-4 text-on-surface font-body-md text-body-md placeholder:text-outline focus:outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container transition-all" placeholder="••••••••" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
              <button className="absolute right-4 top-1/2 -translate-y-1/2 text-outline hover:text-on-surface transition-colors" type="button">
                <span className="material-symbols-outlined text-[20px]">visibility_off</span>
              </button>
            </div>
          </div>

          <div className="flex flex-col gap-xs">
            <label className="font-label-md text-label-md text-on-surface-variant uppercase">Xác nhận lại mật khẩu</label>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline group-focus-within:text-primary-container transition-colors">lock_reset</span>
              <input className="w-full bg-surface-container-lowest border border-outline rounded-xl py-3 pl-12 pr-4 text-on-surface font-body-md text-body-md placeholder:text-outline focus:outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container transition-all" placeholder="••••••••" type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} required />
            </div>
          </div>

          <button className="mt-4 w-full bg-primary-container text-[#ffffff] font-label-md text-label-md uppercase tracking-wide py-4 rounded-xl shadow-[0_4px_20px_rgba(255,107,0,0.25)] hover:shadow-[0_6px_25px_rgba(255,107,0,0.4)] active:scale-[0.98] transition-all flex justify-center items-center gap-2" type="submit" disabled={loading}>
            {loading ? 'Đang tạo tài khoản...' : 'Tạo tài khoản mới'}
            {!loading && <span className="material-symbols-outlined text-[18px]">arrow_forward</span>}
          </button>
        </form>

        {/* Social Sign Up */}
        <div className="flex flex-col gap-4 w-full">
          <div className="flex items-center gap-4">
            <div className="h-[1px] flex-1 bg-outline-variant"></div>
            <span className="font-label-md text-label-md text-on-surface-variant uppercase text-[10px]">Hoặc tiếp tục với</span>
            <div className="h-[1px] flex-1 bg-outline-variant"></div>
          </div>
          <div className="flex gap-4">
            <button className="flex-1 flex justify-center items-center py-3 border border-outline-variant rounded-xl bg-surface-container-lowest hover:bg-surface-container transition-colors" type="button">
              <span className="material-symbols-outlined text-on-surface">account_circle</span>
            </button>
            <button className="flex-1 flex justify-center items-center py-3 border border-outline-variant rounded-xl bg-surface-container-lowest hover:bg-surface-container transition-colors" type="button">
              <span className="material-symbols-outlined text-on-surface">ios</span>
            </button>
          </div>
        </div>

        {/* Footer Link */}
        <div className="text-center mt-4">
          <p className="font-body-md text-body-md text-on-surface-variant">
            Đã có tài khoản? 
            <Link className="text-primary hover:text-primary-container transition-colors font-semibold ml-1" to="/login">Đăng nhập</Link>
          </p>
        </div>
      </main>
    </>
  );
};

export default Signup;
