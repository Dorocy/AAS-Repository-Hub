/*
 * 파일명: src/app/page.tsx
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
import { getPublishedCount } from "@/api";
import AASSearchBar from "@/components/feature/app/AASSearchBar";

export const metadata = { title: "KETI AAS Repository Hub" };
export const dynamic = "force-dynamic";

export default async function Home() {
  let publishedCount = await getPublishedCount();
  if (Array.isArray(publishedCount)) {
    publishedCount = publishedCount.reduce((prev, curr) => {
      prev[curr.ty] = curr;
      return prev;
    }, {});
  }

  return (
    <>
      {/*begin::Toolbar*/}
      <div className="toolbar py-5 py-lg-5 mb-0" id="kt_toolbar">
        {/*begin::Container*/}
        <div id="kt_toolbar_container" className="container-xxl py-5">
          {/*begin::Row*/}
          <div className="row gy-0 gx-10">
            <div className="col-xl-12 mb-2">
              <form action="#">
                {/*begin::Card*/}
                <AASSearchBar />
                {/*end::Card*/}
              </form>
            </div>
          </div>

          <div className="row gy-0 gx-10">
            <div className="col-xl-4">
              <div className="card card-flush h-lg-100">
                {/*begin::Body*/}
                <div className="card-body">
                  {/*begin::Item*/}
                  <a href="/aas">
                    <div className="d-flex flex-stack">
                      {/*begin::Section*/}
                      <div className="text-gray-700 fw-semibold fs-6 me-2">
                        <i className="fa-regular fa-file-lines"></i> AAS
                        Templates
                      </div>
                      {/*end::Section*/}
                      {/*begin::Statistics*/}
                      <div className="d-flex align-items-senter">
                        {publishedCount?.["aasmodel"]?.["is_new"] && (
                          <span className="badge badge-light-success me-2">
                            New
                          </span>
                        )}
                        {/*begin::Number*/}
                        <span className="text-gray-900 fw-bolder fs-6">
                          {publishedCount?.["aasmodel"]?.["cnt"] ?? "0"}
                        </span>
                        {/*end::Number*/}
                      </div>
                      {/*end::Statistics*/}
                    </div>
                  </a>
                  {/*end::Item*/}
                </div>
                {/*end::Body*/}
              </div>
            </div>

            <div className="col-xl-4">
              <div className="card card-flush h-lg-100">
                {/*begin::Body*/}
                <div className="card-body">
                  {/*begin::Item*/}
                  <a href="/submodel">
                    <div className="d-flex flex-stack">
                      {/*begin::Section*/}
                      <div className="text-gray-700 fw-semibold fs-6 me-2">
                        <i className="fa-regular fa-file"></i> Submodel Template
                      </div>
                      {/*end::Section*/}
                      {/*begin::Statistics*/}
                      <div className="d-flex align-items-senter">
                        {publishedCount?.["submodel"]?.["is_new"] && (
                          <span className="badge badge-light-success me-2">
                            New
                          </span>
                        )}
                        {/*begin::Number*/}
                        <span className="text-gray-900 fw-bolder fs-6">
                          {publishedCount?.["submodel"]?.["cnt"] ?? "0"}
                        </span>
                        {/*end::Number*/}
                      </div>
                      {/*end::Statistics*/}
                    </div>
                  </a>
                  {/*end::Item*/}
                </div>
                {/*end::Body*/}
              </div>
            </div>

            <div className="col-xl-4">
              <div className="card card-flush h-lg-100">
                {/*begin::Body*/}
                <div className="card-body">
                  {/*begin::Item*/}
                  <a href="/instance">
                    <div className="d-flex flex-stack">
                      {/*begin::Section*/}
                      <div className="text-gray-700 fw-semibold fs-6 me-2">
                        <i className="fa-regular fa-user"></i> AAS Instances
                      </div>
                      {/*end::Section*/}
                      {/*begin::Statistics*/}
                      <div className="d-flex align-items-senter">
                        {publishedCount?.["instance"]?.["is_new"] && (
                          <span className="badge badge-light-success me-2">
                            New
                          </span>
                        )}
                        {/*begin::Number*/}
                        <span className="text-gray-900 fw-bolder fs-6">
                          {publishedCount?.["instance"]?.["cnt"] ?? "0"}
                        </span>
                        {/*end::Number*/}
                      </div>
                      {/*end::Statistics*/}
                    </div>
                  </a>
                  {/*end::Item*/}
                </div>
                {/*end::Body*/}
              </div>
            </div>
          </div>
          {/*end::Row*/}
        </div>
        {/*end::Container*/}
      </div>

      <div className="py-5 py-lg-5" id="kt_toolbar">
        {/*begin::Container*/}
        <div id="kt_toolbar_container" className="container-xxl py-5">
          {/*begin::Row*/}
          <div className="row gy-0 gx-10">
            <div className="col-xl-12">
              {/*begin::Engage widget 2*/}
              <div className="card card-xl-stretch bg-body mb-5 mb-xl-0">
                {/*begin::Body*/}
                <div className="card-body d-flex flex-column flex-lg-row flex-stack p-lg-15">
                  {/*begin::Info*/}
                  <div className="d-flex flex-column justify-content-center align-items-center align-items-lg-start me-10 text-center text-lg-start">
                    {/*begin::Title*/}
                    <h3 className="fs-2hx line-height-lg mb-5">
                      <span className="fs-3hx">AAS Repository Hub</span>{" "}
                      <span style={{ fontWeight: "100" }}>
                        for Industrial Digital Twin
                      </span>
                    </h3>
                    {/*end::Title*/}
                    <div className="fs-4 text-muted mb-7">
                      serves as a central platform that supports the efficient
                      creation, management, and operation of digital twins
                      <br />
                      for industrial assets, based on AAS(Asset administration
                      Shell) standard
                    </div>
                    <a
                      href="/about"
                      className="btn btn-success fw-semibold px-6 py-3"
                    >
                      About AAS Repository Hub
                    </a>
                  </div>
                  {/*end::Info*/}
                  {/*begin::Illustration*/}
                  <img
                    src="/assets/media/aas/aas_main_ob.png"
                    alt=""
                    className="mw-200px mw-lg-250px mt-lg-n10"
                  />
                  {/*end::Illustration*/}
                </div>
                {/*end::Body*/}
              </div>
              {/*end::Engage widget 2*/}
            </div>
          </div>
          {/*end::Row*/}
        </div>
        {/*end::Container*/}
      </div>
      {/*end::Toolbar*/}

      {/*begin::Container*/}
      <div
        id="kt_content_container"
        className="d-flex flex-column-fluid align-items-start container-xxl"
      >
        {/*begin::Post*/}
        <div className="content flex-row-fluid" id="kt_content">
          {/*begin::Row*/}
          <div className="row gy-0 gx-10">
            {/*begin::Col*/}
            <div className="col-xl-12">
              {/*begin::General Widget 1*/}
              <div className="mb-10">
                {/*begin::Tabs*/}
                <ul className="nav row mb-10">
                  <li className="nav-item col-12 col-lg mb-5 mb-lg-0">
                    <a
                      href="/aas"
                      className="nav-link btn btn-flex btn-color-gray-500 btn-outline btn-active-primary d-flex flex-grow-1 flex-column flex-center py-5 h-1250px h-lg-175px"
                    >
                      <i className="ki-duotone ki-abstract-26 fs-3hx mb-5 mx-0">
                        <span className="path1"></span>
                        <span className="path2"></span>
                      </i>
                      <span className="fs-2 text-success">
                        Unified <br />
                        AAS Template Hub
                      </span>
                    </a>
                  </li>
                  <li className="nav-item col-12 col-lg mb-5 mb-lg-0">
                    <a
                      href="/aas"
                      className="nav-link btn btn-flex btn-color-gray-500 btn-outline btn-active-primary d-flex flex-grow-1 flex-column flex-center py-5 h-1250px h-lg-175px"
                    >
                      <i className="ki-duotone ki-element-11 fs-3hx mb-5 mx-0">
                        <span className="path1"></span>
                        <span className="path2"></span>
                        <span className="path3"></span>
                        <span className="path4"></span>
                      </i>
                      <span className="fs-2 text-success">
                        Compliance <br />
                        with Standard
                      </span>
                    </a>
                  </li>
                  <li className="nav-item col-12 col-lg mb-5 mb-lg-0">
                    <a
                      href="/aas"
                      className="nav-link btn btn-flex btn-color-gray-500 btn-outline btn-active-primary d-flex flex-grow-1 flex-column flex-center py-5 h-1250px h-lg-175px"
                    >
                      <i className="ki-duotone ki-briefcase fs-3hx mb-5 mx-0">
                        <span className="path1"></span>
                        <span className="path2"></span>
                      </i>
                      <span className="fs-2 text-success">
                        Simplified AAS <br />
                        Generation and Deployment
                      </span>
                    </a>
                  </li>
                  <li className="nav-item col-12 col-lg mb-5 mb-lg-0">
                    <a
                      href="/aas"
                      className="nav-link btn btn-flex btn-color-gray-500 btn-outline btn-active-primary d-flex flex-grow-1 flex-column flex-center py-5 h-1250px h-lg-175px"
                    >
                      <i className="ki-duotone ki-chart-simple fs-3hx mb-5 mx-0">
                        <span className="path1"></span>
                        <span className="path2"></span>
                        <span className="path3"></span>
                        <span className="path4"></span>
                      </i>
                      <span className="fs-2 text-success">
                        Scalability <br />
                        through API Support
                      </span>
                    </a>
                  </li>
                </ul>

                <div className="mb-19 mt-15">
                  {/*begin::Top*/}
                  <div className="text-center mb-12">
                    {/*begin::Title*/}
                    <h3 className="fs-2hx text-gray-900 mb-5">About</h3>
                    {/*end::Title*/}
                    {/*begin::Text*/}
                    <div className="fs-5 text-muted fw-semibold">
                      AAS Repository Hub
                    </div>
                    {/*end::Text*/}
                  </div>
                  {/*end::Top*/}
                  {/*begin::Row*/}
                  <div className="row g-10">
                    <div className="col-md-12">
                      <iframe
                        className="embed-responsive-item rounded h-300px w-100"
                        src="https://www.youtube.com/embed/3Km1DXxn0BQ?si=vYGDRr6XdbnEp0UY"
                        allowFullScreen={true}
                      ></iframe>
                    </div>
                  </div>
                  {/*end::Row*/}
                </div>
              </div>
              {/*end::General Widget 1*/}
            </div>
            {/*end::Col*/}
          </div>
          {/*end::Row*/}
        </div>
        {/*end::Post*/}
      </div>
      {/*end::Container*/}
    </>
  );
}
