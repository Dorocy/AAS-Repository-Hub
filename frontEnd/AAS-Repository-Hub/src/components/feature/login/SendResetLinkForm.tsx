import { sendPasswordResetEmail } from "@/api";
import { IconX } from "@tabler/icons-react";
import React, { useState } from "react";

function SendResetLinkForm() {
  const [email, setEmail] = useState("");
  const [emailError, setEmailError] = useState("");

  const [loading, setLoading] = useState(false);

  // 이메일 유효성 검사 함수 추가
  const isValidEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const onChangeEmail = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setEmail(value);

    if (!isValidEmail(value)) {
      setEmailError("Please enter a valid email address.");
    } else {
      setEmailError("");
    }
  };

  const onClickSendResetPassword = async () => {
    // 비밀번호 초기화 링크 전송
    try {
      setLoading(true);

      const result = await sendPasswordResetEmail(email);
    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };
  return (
    <>
      <h2
        style={{
          marginBottom: "20px",
          font: 'bold 24px / 29px "Mona Sans", "Helvetica Neue", Helvetica, Arial, sans-serif',
        }}
      >
        Forgot password?
      </h2>
      <div
        style={{
          font: 'normal 14px/20px "Mona Sans", "Helvetica Neue", Helvetica, Arial, sans-serif',
        }}
      >
        <p>
          Enter the email address you used to sign up, and we’ll send you a
          secure link to reset your password.
        </p>
      </div>
      <div>
        <label
          htmlFor="email"
          className="form-label"
          style={{
            display: "block",
            margin: "14px 0 4px",
            color: "#0d0c22",
            font: 'bold 15px / 24px "Mona Sans", "Helvetica Neue", Helvetica, Arial, sans-serif',
          }}
        >
          Email
        </label>
        <input
          type="text"
          id="email"
          autoComplete="off"
          className="form-control bg-transparent"
          value={email}
          onChange={onChangeEmail}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              onClickSendResetPassword();
            }
          }}
        />
        {emailError && (
          <div className="small mt-1">
            <span className={"text-danger"}>
              <IconX size={"1.25rem"} />
            </span>
            <span className="mx-1">{emailError}</span>
          </div>
        )}
      </div>

      <button
        className="btn btn-sm btn-dark mt-2 w-100"
        disabled={email === "" || emailError !== "" || loading}
        onClick={onClickSendResetPassword}
      >
        <span className="indicator-label">Send Reset Link</span>
      </button>
    </>
  );
}

export default SendResetLinkForm;
