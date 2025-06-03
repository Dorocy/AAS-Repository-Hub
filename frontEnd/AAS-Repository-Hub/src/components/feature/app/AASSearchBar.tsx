"use client";

import { useRef, useState } from "react";
import AASSearchPreview from "../model/AASSearchPreivew";
import SearchBox from "@/components/SearchBox";
import CustomCombobox from "@/components/CustomCombobox";
import { getCodeList } from "@/api";
import { useQuery } from "@tanstack/react-query";
import { Combobox, useCombobox } from "@mantine/core";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { ROUTES } from "@/constants/routes";
import CategoryCombobox from "@/components/CategoryCombobox";

export default function AASSearchBar() {
  const router = useRouter();
  const combobox = useCombobox({
    onDropdownClose: () => combobox.resetSelectedOption(),
  });

  // 검색 박스 상태 값
  const [searchState, setSearchState] = useState({
    category_seq: "",
    searchKey: "",
  });

  // enter or click button
  const searchRef = useRef({
    searchKey: "",
  });

  const { data: categorys } = useQuery({
    queryKey: ["common/code"],
    queryFn: () => getCodeList("category"),
  });

  const handleSearch = () => {
    router.push(`${ROUTES.AASMODEL.LIST}?title=${searchRef.current.searchKey}`);
  };

  return (
    <>
      <SearchBox onSearch={handleSearch}>
        <div className="col-lg-3 d-flex align-items-center mb-lg-0">
          <i className="ki-outline ki-element-11 fs-1 text-gray-500 me-1"></i>

          <CategoryCombobox
            className="border-0"
            value={searchState.category_seq}
            setValue={(value) =>
              setSearchState((prev) => ({
                ...prev,
                category_seq: value ?? "",
                searchKey: searchRef.current.searchKey,
              }))
            }
          />
        </div>

        {/* Search Input */}
        <div className="position-relative w-md-400px me-md-2">
          <i className="ki-outline ki-magnifier fs-3 text-gray-500 position-absolute top-50 translate-middle ms-6"></i>
          <input
            type="text"
            className="form-control form-control-solid ps-10"
            name="search"
            onChange={(e) => {
              searchRef.current.searchKey = e.target.value;
            }}
            onKeyDown={(e) => {
              if (e.key == "Enter") {
                handleSearch();
              }
            }}
            placeholder="Please enter a search term"
          />
        </div>
      </SearchBox>
    </>
  );
}
