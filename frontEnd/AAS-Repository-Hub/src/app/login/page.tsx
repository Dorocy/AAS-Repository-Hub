/*
 * 파일명: src/app/login.tsx
 * 작성자: 김태훈
 * 작성일: 2024-03-15
 * 최종수정일: 2024-03-29
 *
 * 저작권: (c) 2025 IMPIX. 모든 권리 보유.
 *
 * 설명: KETI AAS Repository Hub의 메인 페이지입니다.
 * 이 페이지는 다음과 같은 주요 기능을 제공합니다:
 * - AAS 템플릿, 서브모델, 인스턴스에 대한 통계 및 빠른 접근
 * - 통합 검색 기능
 * - KETI AAS Repository Hub 소개 및 주요 기능 설명
 * - 제품 소개 비디오
 */

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ROUTES } from "@/constants/routes";
import { showToast } from "@/utils/toast";

import { useAuth } from "@/contexts/AuthContext";
import { modals } from "@mantine/modals";
import { Input, TextInput } from "@mantine/core";
import SendResetLinkForm from "@/components/feature/login/SendResetLinkForm";

export default function Login() {
  const { login, loginWithSocial } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const onChangeEmail = (e) => {
    setEmail(e.target.value);
  };
  const onChangePassword = (e) => {
    setPassword(e.target.value);
  };

  const onClickLogin = () => {
    if (email == "") {
      return showToast.error("Please enter email");
    }
    if (password == "") {
      return showToast.error("Please enter password");
    }
    login(email, password);
  };

  return (
    <>
      <div className="d-flex flex-column flex-root">
        {/* begin::Authentication - Sign-in */}
        <div className="d-flex flex-column flex-lg-row flex-column-fluid">
          {/* begin::Body*/}
          <div className="d-flex flex-column flex-lg-row-fluid w-lg-50 p-10 order-2 order-lg-1">
            {/* begin::Form*/}
            <div className="d-flex flex-center flex-column flex-lg-row-fluid">
              {/* begin::Wrapper*/}
              <div className="w-lg-500px p-10">
                {/* begin::Form*/}
                {/* begin::Heading*/}
                <div className="text-center mb-11">
                  {/* begin::Title*/}
                  <h1 className="text-gray-900 fw-bolder mb-3">LOG IN</h1>
                  {/* end::Title*/}
                  {/* begin::Subtitle*/}
                  <div className="text-gray-500 fw-semibold fs-6">
                    KETI AAS Repository Hub
                  </div>
                  {/* end::Subtitle=*/}
                </div>
                {/* begin::Heading*/}
                {/* begin::Login options*/}
                <div className="row g-3 mb-9">
                  {/* begin::Col*/}
                  <div className="col-md-6">
                    {/* begin::Google link=*/}
                    <button
                      className="btn btn-flex btn-outline btn-text-gray-700 btn-active-color-primary bg-state-light flex-center text-nowrap w-100"
                      onClick={() => {
                        loginWithSocial("google");
                      }}
                    >
                      <img
                        alt="Logo"
                        src="assets/media/svg/brand-logos/google-icon.svg"
                        className="h-15px me-3"
                      />
                      Sign in with Google
                    </button>
                    {/* end::Google link=*/}
                  </div>
                  {/* end::Col*/}
                  {/* begin::Col*/}
                  <div className="col-md-6">
                    {/* begin::Google link=*/}
                    <button
                      className="btn btn-flex btn-outline btn-text-gray-700 btn-active-color-primary bg-state-light flex-center text-nowrap w-100"
                      onClick={() => {
                        loginWithSocial("naver");
                      }}
                    >
                      <img
                        alt="Logo"
                        src="assets/media/svg/brand-logos/naver_icon.svg"
                        className="theme-light-show h-15px me-3"
                      />
                      Sign in with naver
                    </button>
                    {/* end::Google link=*/}
                  </div>
                  {/* end::Col*/}
                </div>
                {/* end::Login options*/}
                {/* begin::Separator*/}
                <div className="separator separator-content my-14">
                  <span className="w-125px text-gray-500 fw-semibold fs-7">
                    Or with email
                  </span>
                </div>
                {/* end::Separator*/}
                {/* begin::Input group=*/}
                <div className="fv-row mb-8">
                  {/* begin::Email*/}
                  <input
                    type="text"
                    placeholder="Email"
                    name="email"
                    autoComplete="off"
                    className="form-control bg-transparent"
                    onChange={onChangeEmail}
                    onKeyDown={(e) => {
                      if (e.key == "Enter") {
                        onClickLogin();
                      }
                    }}
                  />
                  {/* end::Email*/}
                </div>
                {/* end::Input group=*/}
                <div className="fv-row mb-3">
                  {/* begin::Password*/}
                  <input
                    type="password"
                    placeholder="Password"
                    name="password"
                    autoComplete="off"
                    className="form-control bg-transparent"
                    onChange={onChangePassword}
                    onKeyDown={(e) => {
                      if (e.key == "Enter") {
                        onClickLogin();
                      }
                    }}
                  />
                  {/* end::Password*/}
                  {/* begin::Sign up*/}
                  <div style={{ display: "flex", justifyContent: "flex-end" }}>
                    <a
                      className="menu-title"
                      style={{
                        cursor: "pointer",
                      }}
                      onClick={(e) => {
                        e.preventDefault();

                        modals.open({
                          closeOnClickOutside: false,
                          closeOnEscape: false,
                          children: <SendResetLinkForm />,
                        });
                      }}
                    >
                      Forgot?
                    </a>
                  </div>
                </div>

                {/* end::Input group=*/}
                {/* begin::Wrapper*/}
                <div className="d-flex flex-stack flex-wrap gap-3 fs-base fw-semibold mb-8">
                  <div></div>
                  {/* begin::Link*/}
                  {/* <a className="link-primary">패스워드 찾기 ?</a>*/}
                  {/* end::Link*/}
                </div>
                {/* end::Wrapper*/}
                {/* begin::Submit button*/}
                <div className="d-grid mb-10">
                  <button
                    id="kt_sign_in_submit"
                    className="btn btn-primary"
                    onClick={onClickLogin}
                  >
                    {/* begin::Indicator label*/}
                    <span className="indicator-label">LOG IN</span>
                    {/* end::Indicator label*/}
                    {/* begin::Indicator progress*/}
                    <span className="indicator-progress">
                      Please wait...
                      <span className="spinner-border spinner-border-sm align-middle ms-2"></span>
                    </span>
                    {/* end::Indicator progress*/}
                  </button>
                </div>
                {/* end::Submit button*/}
                {/* begin::Sign up*/}
                <div className="text-gray-500 text-center fw-semibold fs-6">
                  Not a Member yet?
                  <Link href={ROUTES.SIGNUP} className="menu-title">
                    Sign up
                  </Link>
                </div>
                {/* end::Sign up*/}
                {/* end::Form*/}
              </div>
              {/* end::Wrapper*/}
            </div>
            {/* end::Form*/}
            {/* begin::Footer*/}

            {/* end::Footer*/}
          </div>
          {/* end::Body*/}
          {/* begin::Aside*/}
          <div
            className="d-flex flex-lg-row-fluid w-lg-50 bgi-size-cover bgi-position-center order-1 order-lg-2"
            style={{ backgroundImage: "url(/assets/media/aas/auth-bg.png)" }}
          >
            {/* begin::Content*/}
            <div className="d-flex flex-column flex-center py-7 py-lg-15 px-5 px-md-15 w-100">
              {/* begin::Logo*/}
              <a href={ROUTES.HOME} className="mb-0 mb-lg-12">
                <img
                  alt="Logo"
                  src="assets/media/logos/keti_logo_w.png"
                  className="h-60px h-lg-75px"
                />
              </a>
              {/* end::Logo*/}
              {/* begin::Image
						<img className="d-none d-lg-block mx-auto mb-10 mb-lg-20" src="assets/media/aas/aas_main.png" alt="" />*/}
              {/* end::Image*/}
              {/* begin::Title*/}
              <h1 className="d-none d-lg-block text-white fs-2qx fw-bolder text-center mb-7">
                KETI AAS Repository Hub
              </h1>
              {/* end::Title*/}
              {/* begin::Text*/}
              <div className="d-none d-lg-block text-white fs-base text-center">
                AAS Repository Hub for Industrial Digital Twin
              </div>
              {/* end::Text*/}
            </div>
            {/* end::Content*/}
          </div>
          {/* end::Aside*/}
        </div>
        {/* end::Authentication - Sign-in*/}
      </div>
    </>
  );
}
