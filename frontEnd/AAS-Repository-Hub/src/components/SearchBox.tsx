import React from "react";

interface SearchBoxProps {
  onSearch: () => void;
  children?: React.ReactNode;
}

const SearchBox: React.FC<SearchBoxProps> = ({ onSearch, children }) => {
  return (
    <div className="card mb-7">
      <div className="card-body">
        <div className="d-flex align-items-center gap-4">
          {/* 🔽 동적으로 주입되는 옵션 컴포넌트들 */}
          {children}

          {/* 🔍 Search 버튼 */}
          <button type="button" className="btn btn-primary" onClick={onSearch}>
            Search
          </button>
        </div>
      </div>
    </div>
  );
};

export default SearchBox;
