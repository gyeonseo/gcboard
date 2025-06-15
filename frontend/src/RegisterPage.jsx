import { useState } from "react";
import axios from "axios";
import "./RegisterPage.css";


export default function RegisterPage() { 

  const [form, setForm] = useState({
    email: "",
    password: "",
    nickname: ""
  });

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
     try {
    console.log("요청 데이터:", form);
    const res = await axios.post("http://localhost:5000/api/auth/register", form);
    console.log("응답:", res.data);
    alert("회원가입 성공! 이메일 인증을 확인하세요.");
  } catch (err) {
    console.log("에러 발생 - 전체 에러 객체:", err);
    const msg = err.response?.data?.message || err.message || "회원가입 실패";
    alert("회원가입 실패: " + msg);
  }
  };

  return (
    <div className="form-container">
      <h2>회원가입</h2>
      <form onSubmit={handleSubmit}>
        <input type="email" name="email" placeholder="이메일" onChange={handleChange} required />
        <input type="password" name="password" placeholder="비밀번호" onChange={handleChange} required />
        <input type="text" name="nickname" placeholder="닉네임 (선택)" onChange={handleChange} />
        <button type="submit">가입하기</button>
      </form>
    </div>
  );
}
