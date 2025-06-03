/*
 * 파일명: src/app/user/page.tsx
 * 작성자: 김태훈
 * 작성일: 2024-03-15
 * 최종수정일: 2024-03-29
 *
 * 저작권: (c) 2025 IMPIX. 모든 권리 보유.
 *
 * 설명: 사용자 권한 관리 페이지를 제공합니다.
 */

"use client";

import React, { useRef, useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { getCodeList, getUserList, upsertUser } from "@/api";
import {
  MantineReactTable,
  MRT_PaginationState,
  MRT_RowData,
  useMantineReactTable,
} from "mantine-react-table";
import { ROUTES } from "@/constants/routes";
import { confirmSave } from "@/utils/modal";
import CustomCombobox from "@/components/CustomCombobox";
import SearchBox from "@/components/SearchBox";
import { Badge } from "@mantine/core";

export interface User {
  AAS_Seq_No: number;
  user_seq: number;
  user_id: string;
  pw_hash: string;
  user_name: string;
  status: "Y" | "N";
  user_phonenumber: string | null;
  start_timestamp: string; // ISO 타임스탬프 문자열
  socialaccount_seq: number | null;
  social_id: string | null;
  social_in_id: string | null;
  socialprovider_seq: number | null;
  socialprovider_name: string | null;
  user_group_seq: number | string;
  user_group_name: string;
  user_photo_url: string;
}

export default function Page() {
  const { data: groups = [] } = useQuery({
    queryKey: ["common/code", "group"],
    queryFn: () => getCodeList("group"),
  });

  // // 검색 박스 상태 값
  const [searchState, setSearchState] = useState({
    user_group_seq: "",
    searchKey: "",
  });

  const [userState, setUserState] = useState({});

  const [pagination, setPagination] = useState<MRT_PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  // enter or click button
  const searchRef = useRef({
    searchKey: "",
  });

  const {
    data: users,
    isFetching: isFetchingUsers,
    isSuccess,
    refetch,
  } = useQuery({
    queryKey: [pagination, searchState],
    queryFn: () =>
      getUserList({
        pageNumber: pagination.pageIndex + 1,
        pageSize: pagination.pageSize,
        searchParams: {
          ...searchState,
          p: "p",
        },
      }),
  });

  const handleSearch = () => {
    const keyword = searchRef.current.searchKey;

    if (searchState.searchKey === keyword) {
      refetch();
    } else {
      setSearchState((prev) => ({ ...prev, searchKey: keyword }));
    }
  };

  const usersData: User[] = users?.data ?? [];
  const table = useMantineReactTable({
    columns: [
      {
        accessorKey: "user_id",
        header: "NAME / ID",
        size: 300,
        Cell: ({ row }) => {
          return (
            <div
              className="d-flex align-items-center"
              style={{ overflow: "scroll" }}
            >
              <div className="me-5 position-relative">
                <div className="symbol symbol-35px symbol-circle">
                  <img alt="Pic" src="/assets/media/avatars/blank.png" />
                </div>
              </div>
              <div className="d-flex flex-column justify-content-center">
                <Link
                  href={ROUTES.USER.VIEW(row.original.user_seq)}
                  className="mb-1 text-gray-800 text-hover-primary"
                >
                  {row.original.user_name}
                </Link>
                <div className="fw-semibold fs-7 text-gray-500">
                  {row.original.user_id}
                </div>
              </div>
            </div>
          );
        },
      },
      {
        accessorKey: "socialprovider_name",
        header: "Social",
      },
      {
        accessorKey: "start_timestamp",
        header: "Create Date",
        Cell: ({ cell }) =>
          new Date(cell.getValue<string>()).toLocaleDateString(),
      },
      {
        accessorKey: "user_group_name",
        header: "Role",
      },
      {
        accessorKey: "status_nm",
        header: "Status",
        Cell: ({ cell }) => {
          return (
            <>
              <Badge
                radius={"sm"}
                color={cell.getValue() == "Activate" ? "green" : "red.4"}
              >
                {cell.getValue()}
              </Badge>
            </>
          );
        },
      },
      {
        accessorKey: "edit",
        header: "Edit",
        size: 100,
        Cell: ({ row }) => (
          <Link
            href={ROUTES.USER.EDIT(row.original.user_seq)}
            className="btn btn-light-success btn-sm"
          >
            <i className="fa-regular fa-pen-to-square"></i> Edit
          </Link>
        ),
      },
    ],
    data: usersData,
    rowCount: users?.recordsTotal ?? 0,
    state: {
      pagination,
      showSkeletons: isFetchingUsers,
    },
    enableColumnPinning: true,
    initialState: {
      columnPinning: {
        // right: ["externalButtons"],
      },
    },
    layoutMode: "grid",
    paginationDisplayMode: "pages",
    manualPagination: true,
    enablePagination: true,
    onPaginationChange: setPagination,
  });

  return (
    <>
      {/*begin::Toolbar*/}
      <div className="toolbar py-5 py-lg-5" id="kt_toolbar">
        {/*begin::Container*/}
        <div
          id="kt_toolbar_container"
          className="container-xxl d-flex flex-stack flex-wrap"
        >
          {/*begin::Page title*/}
          <div className="page-title d-flex flex-column me-3">
            {/*begin::Title*/}
            <h1 className="d-flex text-gray-900 fw-bold my-1 fs-3">
              Authority
            </h1>
            {/*end::Title*/}
            {/*begin::Breadcrumb*/}
            <ul className="breadcrumb breadcrumb-dot fw-semibold text-gray-600 fs-7 my-1">
              {/*begin::Item*/}
              <li className="breadcrumb-item text-gray-600">
                <Link
                  href={ROUTES.HOME}
                  className="text-gray-600 text-hover-primary"
                >
                  Home
                </Link>
              </li>
              {/*end::Item*/}
              {/*begin::Item*/}
              <li className="breadcrumb-item text-gray-600">Authority</li>
              {/*end::Item*/}
            </ul>
            {/*end::Breadcrumb*/}
          </div>
          {/*end::Page title*/}
          {/*begin::Actions*/}
          <div className="d-flex align-items-center py-2 py-md-1">
            {/*begin::Button*/}
            {/*end::Button*/}
          </div>
          {/*end::Actions*/}
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
          <div>
            <div>
              <SearchBox onSearch={handleSearch}>
                <div className="col-lg-3 d-flex align-items-center mb-lg-0">
                  <i className="ki-outline ki-element-11 fs-1 text-gray-500 me-1"></i>

                  <CustomCombobox
                    border={false}
                    className="form-control border-0 flex-grow-1"
                    data={[{ id: "all", text: "Group All" }, ...groups]}
                    mappingFn={(item) => ({ value: item.id, label: item.text })}
                    value={searchState.user_group_seq}
                    onChange={(value) =>
                      setSearchState((prev) => ({
                        ...prev,
                        user_group_seq: value ?? "",
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
            </div>

            <div className="d-flex flex-wrap flex-stack pb-7">
              {/*begin::Title*/}
              <div className="d-flex flex-wrap align-items-center my-1">
                <h3 className="fw-bold me-5 my-1">
                  5 results found
                  <span className="text-gray-500 fs-6">↓</span>
                </h3>
              </div>
              {/*end::Title*/}
            </div>

            <div id="kt_project_users_table_pane">
              {/*begin::Card*/}
              <div className="card card-flush">
                {/*begin::Card body*/}
                <div className="card-body pt-0">
                  <MantineReactTable table={table} />
                  {/*begin::Table container*/}

                  {/*end::Table container*/}
                </div>
                {/*end::Card body*/}
              </div>
              {/*end::Card*/}
            </div>
          </div>
        </div>
        {/*end::Post*/}
      </div>
      {/*end::Container*/}
    </>
  );
}
