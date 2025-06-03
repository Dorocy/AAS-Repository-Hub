/*
 * 파일명: src/components/Header.tsx
 * 작성자: 김태훈
 * 작성일: 2024-03-15
 * 최종수정일: 2024-03-29
 *
 * 저작권: (c) 2025 IMPIX. 모든 권리 보유.
 *
 * 설명: 애플리케이션의 헤더 영역을 구성하는 컴포넌트입니다.
 */
"use client";

import { ROUTES } from "@/constants/routes";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import AASSpotlight from "./feature/app/AASSpotlight";

function Header() {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [mounted, setMounted] = useState(false);
  const router = useRouter();

  const { isAuthenticated } = useAuth();

  const { logout, user: profile } = useAuth();

  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
    // Initialize theme from localStorage or default
    const savedTheme = localStorage.getItem("data-bs-theme") || "light";
    setTheme(savedTheme as "light" | "dark");
    document.documentElement.setAttribute("data-bs-theme", savedTheme);

    const handleClickOutside = (event: MouseEvent) => {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(event.target as Node)
      ) {
        setMenu(false); // ✅ 바깥 클릭 시 닫기
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    document.documentElement.setAttribute("data-bs-theme", newTheme);
    localStorage.setItem("data-bs-theme", newTheme);
  };

  // ---- 로그인 체크 2025.04.18 start ----
  //   const handleLogout = () => {
  //     logout();
  //     router.push('/sign');
  //   };

  //   if (!mounted || !isAuthenticated) {
  //     return null;
  //   }
  // ---- 로그인 체크 2025.04.18 end ----

  const [isOpen, setMenu] = useState(false); // 메뉴의 초기값을 false로 설정

  const toggleMenu = () => {
    setMenu((isOpen) => !isOpen); // on,off 개념 boolean
  };

  if (!mounted) {
    return null;
  }

  return (
    <div
      id="kt_header"
      className="header"
      data-kt-sticky="true"
      data-kt-sticky-name="header"
      data-kt-sticky-offset="{default: '200px', lg: '300px'}"
    >
      {/*begin::Container*/}
      <div className="container-xxl d-flex flex-grow-1 flex-stack">
        {/*begin::Header Logo*/}
        <div className="d-flex align-items-center me-5">
          {/*begin::Heaeder menu toggle*/}
          <div
            className="d-lg-none btn btn-icon btn-active-color-primary w-30px h-30px ms-n2 me-3"
            id="kt_header_menu_toggle"
          >
            <i className="ki-duotone ki-abstract-14 fs-2">
              <span className="path1"></span>
              <span className="path2"></span>
            </i>
          </div>
          {/*end::Heaeder menu toggle*/}
          <Link href={ROUTES.HOME}>
            <img
              alt="Logo"
              src="/assets/media/logos/keti_logo.png"
              className="theme-light-show h-20px h-lg-45px"
            />
            {/* <img alt="Logo" src="/assets/media/logos/keti_logo.png" className="theme-dark-show h-20px h-lg-45px" />  */}
          </Link>
        </div>
        {/*end::Header Logo*/}
        {/*begin::Topbar*/}
        <div className="d-flex align-items-center flex-shrink-0">
          {/*begin::Search*/}
          <AASSpotlight />
          {/*end::Search*/}

          {/*begin::Theme mode*/}
          {/* <div className="d-flex align-items-center ms-3 ms-lg-4">
                  <button 
                    onClick={toggleTheme}
                    className="btn btn-icon btn-color-gray-700 btn-active-color-primary btn-outline btn-active-bg-light w-30px h-30px w-lg-40px h-lg-40px"
                  >
                      <i className={`ki-duotone ki-night-day theme-light-show fs-1 ${theme === 'dark' ? 'd-none' : ''}`}>
                          <span className="path1"></span>
                          <span className="path2"></span>
                          <span className="path3"></span>
                          <span className="path4"></span>
                          <span className="path5"></span>
                          <span className="path6"></span>
                          <span className="path7"></span>
                          <span className="path8"></span>
                          <span className="path9"></span>
                          <span className="path10"></span>
                      </i>
                      <i className={`ki-duotone ki-moon theme-dark-show fs-1 ${theme === 'light' ? 'd-none' : ''}`}>
                          <span className="path1"></span>
                          <span className="path2"></span>
                      </i>
                  </button>
              </div> */}
          {/*end::Theme mode*/}
          {/*begin::User*/}
          <div
            className="d-flex align-items-center ms-3 ms-lg-4"
            style={{ position: "relative" }}
            id="kt_header_user_menu_toggle"
            ref={wrapperRef}
          >
            {/*begin::Menu- wrapper*/}
            {/*begin::User icon(remove this button to use user avatar as menu toggle)*/}
            {!isAuthenticated ? (
              <Link href={ROUTES.LOGIN} className="btn btn-light ">
                Log in
              </Link>
            ) : (
              <button
                onClick={() => toggleMenu()}
                className="btn btn-icon btn-color-gray-700 btn-active-color-primary btn-outline btn-active-bg-light w-30px h-30px w-lg-40px h-lg-40px"
                data-kt-menu-trigger="click"
                data-kt-menu-attach="parent"
                data-kt-menu-placement="bottom-end"
              >
                <i className="ki-duotone ki-user fs-1">
                  <span className="path1"></span>
                  <span className="path2"></span>
                </i>
              </button>
            )}

            {/*end::User icon*/}
            {/*begin::User account menu*/}
            {/* <div className="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-800 menu-state-bg menu-state-color fw-semibold py-4 fs-6 w-275px" data-kt-menu="true"> */}
            <div
              className={isOpen ? "show-menu" : "d-none"}
              data-kt-menu="true"
            >
              {/*begin::Menu item*/}
              <div className="menu-item px-3">
                <div className="menu-content d-flex align-items-center px-3">
                  {/*begin::Avatar*/}
                  <div className="symbol symbol-50px me-5">
                    <img
                      alt="Logo"
                      src={
                        profile?.user_photo_url
                          ? profile.user_photo_url
                          : "/assets/media/avatars/blank.png"
                      }
                    />
                  </div>
                  {/*end::Avatar*/}
                  {/*begin::Username*/}
                  <div className="d-flex flex-column">
                    <div className="fw-bold d-flex align-items-center fs-5">
                      {profile?.user_name}
                      <span className="badge badge-light-success fw-bold fs-8 px-2 py-1 ms-2">
                        {profile?.user_group_name}
                      </span>
                    </div>
                    <a className="fw-semibold text-muted text-hover-primary fs-7">
                      {profile?.user_id}
                    </a>
                  </div>
                  {/*end::Username*/}
                </div>
              </div>
              {/*end::Menu item*/}
              {/*begin::Menu separator*/}
              <div className="separator my-2"></div>
              {/*end::Menu separator*/}
              {/*begin::Menu item*/}
              <div className="menu-item px-5">
                <Link
                  href={ROUTES.USER.VIEW(profile?.user_seq)}
                  onClick={() => toggleMenu()}
                  className="menu-link px-5 text-black"
                >
                  My Profile
                </Link>
              </div>
              {/*end::Menu item*/}
              {/*begin::Menu item*/}
              <div className="menu-item px-5">
                <Link
                  href={ROUTES.INSTANCE.LIST}
                  onClick={() => toggleMenu()}
                  className="menu-link px-5"
                >
                  <span className="menu-text text-black">My AAS Instace</span>
                </Link>
              </div>
              {/*end::Menu item*/}
              {/*begin::Menu item*/}
              {profile?.user_group_seq == 1 && (
                <>
                  <div className="menu-item px-5">
                    <Link
                      href={ROUTES.DISTRIBUTE.LIST}
                      onClick={() => toggleMenu()}
                      className="menu-link px-5 text-black"
                    >
                      Admin : Publish
                    </Link>
                  </div>
                  <div className="menu-item px-5">
                    <Link
                      href={ROUTES.USER.LIST}
                      onClick={() => toggleMenu()}
                      className="menu-link px-5 text-black"
                    >
                      Admin : Authority
                    </Link>
                  </div>
                </>
              )}
              {/*end::Menu item*/}

              {/*begin::Menu separator*/}
              <div className="separator my-2"></div>
              {/*end::Menu separator*/}
              {/*begin::Menu item*/}
              {/*end::Menu item*/}
              {/*begin::Menu item*/}
              <div
                className="menu-item px-5 my-1"
                onClick={() => {
                  toggleMenu();
                  logout();
                }}
              >
                <span className="menu-link px-5 text-black">Log Out</span>
              </div>
              {/*end::Menu item*/}
            </div>
            {/*end::User account menu*/}
            {/*end::Menu wrapper*/}
          </div>
          {/*end::User */}
        </div>
        {/*end::Topbar*/}
      </div>
      {/*end::Container*/}
      {/*begin::Separator*/}
      <div className="separator"></div>
      {/*end::Separator*/}
      {/*begin::Container*/}
      <div
        className="header-menu-container container-xxl d-flex flex-stack h-lg-75px w-100"
        id="kt_header_nav"
      >
        {/*begin::Menu wrapper*/}
        <div
          className="header-menu flex-column flex-lg-row"
          data-kt-drawer="true"
          data-kt-drawer-name="header-menu"
          data-kt-drawer-activate="{default: true, lg: false}"
          data-kt-drawer-overlay="true"
          data-kt-drawer-width="{default:'200px', '300px': '250px'}"
          data-kt-drawer-direction="start"
          data-kt-drawer-toggle="#kt_header_menu_toggle"
          data-kt-swapper="true"
          data-kt-swapper-mode="prepend"
          data-kt-swapper-parent="{default: '#kt_body', lg: '#kt_header_nav'}"
        >
          {/*begin::Menu*/}
          <div
            className="menu menu-rounded menu-column menu-lg-row menu-root-here-bg-desktop menu-active-bg menu-state-primary menu-title-gray-800 menu-arrow-gray-500 align-items-stretch flex-grow-1 my-5 my-lg-0 px-2 px-lg-0 fw-semibold fs-6"
            id="#kt_header_menu"
            data-kt-menu="true"
          >
            <div className="menu-item menu-here-bg menu-lg-down-accordion me-0 me-lg-2">
              <span className="menu-link py-3">
                <a href={ROUTES.AASMODEL.LIST} className="menu-title">
                  AAS Template
                </a>
              </span>
            </div>

            <div className="menu-item menu-lg-down-accordion menu-sub-lg-down-indention me-0 me-lg-2">
              {/*begin:Menu link*/}
              <span className="menu-link py-3">
                <a href={ROUTES.SUBMODEL.LIST} className="menu-title">
                  Submodel Template
                </a>
              </span>
            </div>

            <div className="menu-item menu-lg-down-accordion menu-sub-lg-down-indention me-0 me-lg-2">
              <span className="menu-link py-3">
                <a href={ROUTES.INSTANCE.LIST} className="menu-title">
                  AAS Instance
                </a>
              </span>
            </div>

            <div className="menu-item menu-lg-down-accordion menu-sub-lg-down-indention me-0 me-lg-2">
              {/*begin:Menu link*/}
              <span className="menu-link py-3">
                <a href={ROUTES.ABOUT} className="menu-title">
                  About
                </a>
              </span>
            </div>

            {profile?.user_group_seq == 1 && (
              <>
                <div className="menu-item menu-lg-down-accordion menu-sub-lg-down-indention me-0 me-lg-2">
                  <span className="menu-link py-3">
                    <a href={ROUTES.DISTRIBUTE.LIST} className="menu-title">
                      Publish
                    </a>
                  </span>
                </div>

                <div className="menu-item menu-lg-down-accordion menu-sub-lg-down-indention me-0 me-lg-2">
                  <span className="menu-link py-3">
                    <a href={ROUTES.USER.LIST} className="menu-title">
                      Authority
                    </a>
                  </span>
                </div>
              </>
            )}
          </div>
          {/*end::Menu*/}
          {/*begin::Actions*/}
          <div className="flex-shrink-0 p-4 p-lg-0 me-lg-2">
            <Link
              href={ROUTES.INSTANCE.LIST}
              className="btn btn-sm btn-primary fw-bold w-100 w-lg-auto"
              title=""
            >
              <i className="fa-regular fa-user"></i>
              AAS Instace
            </Link>
          </div>
          {/*end::Actions*/}
        </div>
        {/*end::Menu wrapper*/}
      </div>
      {/*end::Container*/}
    </div>
  );
}

export default Header;
