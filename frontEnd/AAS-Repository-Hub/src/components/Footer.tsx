/*
 * 파일명: src/components/Footer.tsx
 * 작성자: 김태훈
 * 작성일: 2024-03-15
 * 최종수정일: 2024-03-29
 * 
 * 저작권: (c) 2025 IMPIX. 모든 권리 보유.
 * 
 * 설명: 애플리케이션의 푸터 영역을 구성하는 컴포넌트입니다.
 */

function Footer() {
    return <footer className="footer">
        {/*begin::Footer*/}
        <div className="footer py-4 d-flex flex-lg-column" id="kt_footer">
            {/*begin::Container*/}
            <div className="container-xxl d-flex flex-column flex-md-row align-items-center justify-content-between">
                {/*begin::Copyright*/}
                <div className="text-gray-900 order-2 order-md-1">
                    <span className="text-muted fw-semibold me-1">2025&copy;</span>
                    <a href="#" className="text-gray-800 text-hover-primary">KETI AAS Repository Hub</a>
                </div>
                {/*end::Copyright*/}
                {/*begin::Menu*/}
                
                {/*end::Menu*/}
            </div>
            {/*end::Container*/}
        </div>
        {/*end::Footer*/}
    </footer>
}
  
export default Footer