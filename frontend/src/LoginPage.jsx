import { useState } from "react";
import axios from "axios";
import "./LoginPage.css";

export default function LoginPage() {
  const [form, setForm] = useState({ email: "", password: "" });

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      await axios.post("/api/login", form, { withCredentials: true });
      alert("로그인 성공!");
      window.location.href = "/";
    } catch (err) {
      alert("로그인 실패: " + err.response?.data?.message);
    }
  };

  return (
    <div className="login-wrapper">
      <div className="form-container">
        <h2>로그인</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            name="email"
            placeholder="이메일"
            onChange={handleChange}
            required
          />
          <input
            type="password"
            name="password"
            placeholder="비밀번호"
            onChange={handleChange}
            required
          />
          <button type="submit">로그인</button>

          {/* ✅ 하단 로그인 옵션 */}
          <div className="login-options">
            <label className="remember-me">
              로그인 유지
              <input type="checkbox" />
            </label>
            <a href="#" className="find-link">
              아이디/비밀번호 찾기
            </a>
          </div>

          <div className="signup-link">
            <a href="#">회원가입</a>
          </div>
        </form>
      </div>
    </div>
  );
}
