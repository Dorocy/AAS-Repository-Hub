"use client";

import React, { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { resetPassword } from "@/api"; // 실제 비밀번호 재설정 요청 함수
import { showToast } from "@/utils/toast";
import { IconCheck, IconX } from "@tabler/icons-react";
import { ROUTES } from "@/constants/routes";
import { Box } from "@mantine/core";

export default function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const checkPasswordConditions = (password: string) => {
    return [
      { valid: /.{8,}/.test(password), label: "At least 8 characters" },
      { valid: /[A-Za-z]/.test(password), label: "Contains a letter" },
      { valid: /[0-9]/.test(password), label: "Contains a number" },
      { valid: /[!@#$%^&*]/.test(password), label: "Contains a symbol" },
    ];
  };

  const passwordChecks = checkPasswordConditions(password);

  const matchError = confirmPassword && password !== confirmPassword;

  const onClickResetPassword = async () => {
    if (
      !password ||
      !confirmPassword ||
      passwordChecks.some((check) => !check.valid) ||
      matchError ||
      loading
    ) {
      return;
    }
    if (!token) {
      showToast.error("Invalid or missing reset token.");
      return;
    }

    if (password !== confirmPassword) {
      showToast.error("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);
      const result = await resetPassword(token, password);
      setTimeout(() => {
        router.push(ROUTES.LOGIN);
      }, 1500);
    } catch (error: any) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Box
        id="kt_content_container"
        className="d-flex flex-column-fluid "
        pt={"120px"}
        px={{
          base: "5%",
          xs: "20%",
          sm: "25%",
          md: "30%",
          lg: "30%",
          xl: "35%",
        }}
      >
        {/*begin::Post*/}
        <div className="content flex-row-fluid" id="kt_content">
          <h2
            style={{
              marginBottom: "20px",
              font: 'bold 24px / 29px "Mona Sans", "Helvetica Neue", Helvetica, Arial, sans-serif',
            }}
          >
            Reset your password
          </h2>
          <div
            style={{
              font: 'normal 14px/20px "Mona Sans", "Helvetica Neue", Helvetica, Arial, sans-serif',
            }}
          >
            <p>
              Set a new password for your account. Make sure it’s something
              secure and memorable.
            </p>
          </div>

          <div className="mb-1">
            <label
              htmlFor="new-password"
              style={{
                display: "block",
                margin: "14px 0 4px",
                color: "#0d0c22",
                font: 'bold 15px / 24px "Mona Sans", "Helvetica Neue", Helvetica, Arial, sans-serif',
              }}
            >
              New Password
            </label>
            <input
              type="password"
              id="new-password"
              className="form-control bg-transparent"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <div className="d-flex align-items-center mb-2">
            {[...Array(passwordChecks.filter((c) => c.valid).length)].map(
              (_, i) => (
                <div
                  key={i}
                  className="flex-grow-1 bg-active-success rounded h-5px me-2 active"
                ></div>
              )
            )}
            {[...Array(4 - passwordChecks.filter((c) => c.valid).length)].map(
              (_, i) => (
                <div
                  key={i}
                  className="flex-grow-1 bg-secondary rounded h-5px me-2"
                ></div>
              )
            )}
          </div>
          <ul className="text mb-0 px-1 small">
            {passwordChecks.map((check, i) => (
              <li style={{ listStyle: "none" }} key={i}>
                <span className={check.valid ? "text-success" : "text-danger"}>
                  {check.valid ? (
                    <IconCheck size={"1.25rem"} />
                  ) : (
                    <IconX size={"1.25rem"} />
                  )}
                </span>
                <span className={`mx-1`}>{check.label}</span>
              </li>
            ))}
          </ul>

          <label
            htmlFor="confirm-password"
            style={{
              display: "block",
              margin: "14px 0 4px",
              color: "#0d0c22",
              font: 'bold 15px / 24px "Mona Sans", "Helvetica Neue", Helvetica, Arial, sans-serif',
            }}
          >
            Confirm Password
          </label>
          <input
            type="password"
            id="confirm-password"
            className="form-control bg-transparent"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                onClickResetPassword();
              }
            }}
          />
          {matchError && (
            <div className="text-danger mt-1 small">
              Passwords do not match.
            </div>
          )}

          <button
            className="btn btn-sm btn-dark mt-4 w-100"
            disabled={
              !password ||
              !confirmPassword ||
              passwordChecks.some((check) => !check.valid) ||
              matchError ||
              loading
            }
            onClick={onClickResetPassword}
          >
            <span className="indicator-label">Reset Password</span>
          </button>
        </div>
      </Box>
    </>
  );
}
