/*
 * 파일명: src/app/instance/page.tsx
 * 작성자: 김태훈
 * 작성일: 2024-03-15
 * 최종수정일: 2024-03-29
 *
 * 저작권: (c) 2025 IMPIX. 모든 권리 보유.
 *
 * 설명: AAS 인스턴스 목록 페이지를 제공합니다.
 */

"use client";

import React, { Children, useRef, useState } from "react";
import Link from "next/link";
import { getCodeList, getModelList, exportModel, getInstanceList } from "@/api";
import { ROUTES } from "@/constants/routes";
import { Badge, Flex, Anchor, Menu, Text } from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import {
  MRT_PaginationState,
  useMantineReactTable,
  MRT_RowData,
  MantineReactTable,
} from "mantine-react-table";
import CustomCombobox from "@/components/CustomCombobox";
import SearchBox from "@/components/SearchBox";
import { useAuth } from "@/contexts/AuthContext";
import { UserRole } from "@/constants/roles";
import { modals } from "@mantine/modals";
import CategoryCombobox from "@/components/CategoryCombobox";

export default function Page() {
  const { user } = useAuth();
  // 검색 박스 상태 값
  const [searchState, setSearchState] = useState({
    category_seq: "all",
    searchKey: "",
  });

  // enter or click button
  const searchRef = useRef({
    searchKey: "",
  });

  const [pagination, setPagination] = useState<MRT_PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  const { data: categorys = [] } = useQuery({
    queryKey: ["common/code", "category"],
    queryFn: () => getCodeList("category"),
  });

  const {
    data: models,
    isFetching: isFetchingModels,
    isSuccess,
    refetch,
  } = useQuery({
    queryKey: ["aasmodel", pagination, searchState],
    queryFn: () =>
      getInstanceList({
        category_seq: searchState.category_seq,
        pageNumber: pagination.pageIndex + 1,
        pageSize: pagination.pageSize,
        searchParams: {
          ...searchState,
          p: "p",
        },
      }),
  });

  const modelsData = models?.data ?? [];

  const handleExport = (format, model) => {
    exportModel({
      modelType: "instance",
      format,
      modelSeq: model[`instance_seq`],
      filename: model[`instance_name`],
    });
  };

  const handleSearch = () => {
    const keyword = searchRef.current.searchKey;

    if (searchState.searchKey === keyword) {
      refetch();
    } else {
      setSearchState((prev) => ({ ...prev, searchKey: keyword }));
    }
  };

  const table = useMantineReactTable({
    columns: [
      {
        accessorKey: "category_name",
        header: "Category",
        Cell: ({ row }) => (
          <div className="d-flex align-items-center">
            <div className="me-5 position-relative">
              <div className="symbol symbol-35px symbol-circle">
                <span className="symbol-label fw-semibold">
                  <i className="fa-solid fa-list"></i>
                </span>
              </div>
            </div>
            <div className="d-flex flex-column justify-content-center">
              {row.original.category_name}
            </div>
          </div>
        ),
      },
      {
        accessorKey: "instance_name",
        header: "Instance Name",
        Cell: ({ row }) => (
          <div className="d-flex flex-column justify-content-center">
            <Link
              href={ROUTES.INSTANCE.VIEW(row.original.instance_seq)}
              className="mb-1 text-gray-800 text-hover-primary"
            >
              {row.original.instance_name}
            </Link>
          </div>
        ),
      },
      {
        accessorKey: "description",
        header: "Description",
      },
      {
        accessorKey: "aasmodel_template_id",
        header: "Reference Template ID",
      },
      {
        accessorKey: "verification",
        header: "Verification Result",
        size: 120,
        Cell: ({ cell }) => {
          return (
            <Badge
              mt={4}
              mr={4}
              color={cell.getValue() === "success" ? "green" : "red.4"}
              radius="sm"
            >
              {cell.getValue()}
            </Badge>
          );
        },
      },
      ...(user?.user_group_seq <= UserRole.Approvedor
        ? [
            {
              accessorKey: "user_id",
              header: "UserID",
              Cell: ({ cell }) => (
                <Text fz="sm" fw={600}>
                  {cell.getValue()}
                </Text>
              ),
            },
          ]
        : []),
      {
        accessorKey: "file_download",
        header: "File Download",
        size: 140,
        Cell: ({ row }) => (
          <Menu shadow="md" width={200}>
            <Menu.Target>
              <button
                className="btn btn-success btn-sm dropdown-toggle"
                type="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                Export
              </button>
            </Menu.Target>
            <Menu.Dropdown>
              {["json", "xml", "aasx"].map((format) => (
                <Menu.Item
                  key={format}
                  onClick={() => handleExport(format, row.original)}
                >
                  {format}
                </Menu.Item>
              ))}
            </Menu.Dropdown>
          </Menu>
        ),
      },
      {
        accessorKey: "Edit",
        header: "Edit",
        size: 100,
        Cell: ({ row }) => {
          return (
            <Link
              href={ROUTES.INSTANCE.EDIT(row.original.instance_seq)}
              className="btn btn-light-success btn-sm"
            >
              <i className="fa-regular fa-pen-to-square"></i> Edit
            </Link>
          );
        },
      },
    ],
    data: modelsData as MRT_RowData[],
    rowCount: models?.recordsTotal ?? 0,
    state: {
      pagination,
      showSkeletons: isFetchingModels,
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
    <div>
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
              AAS Instance
            </h1>
            {/*end::Title*/}
            {/*begin::Breadcrumb*/}
            <ul className="breadcrumb breadcrumb-dot fw-semibold text-gray-600 fs-7 my-1">
              {/*begin::Item*/}
              <li className="breadcrumb-item text-gray-600">
                <Link href="/" className="text-gray-600 text-hover-primary">
                  Home
                </Link>
              </li>
              {/*end::Item*/}
              {/*begin::Item*/}
              <li className="breadcrumb-item text-gray-600">AAS Instance</li>
              {/*end::Item*/}
            </ul>
            {/*end::Breadcrumb*/}
          </div>
          {/*end::Page title*/}
          {/*begin::Actions*/}
          <div className="d-flex align-items-center py-2 py-md-1">
            {/*begin::Button*/}
            <Link href="/instance/ins" className="btn btn-success fw-bold">
              <i className="fa-solid fa-tablet"></i> Register
            </Link>
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
                  <CategoryCombobox
                    className="border-0"
                    value={searchState.category_seq}
                    setValue={(value) =>
                      setSearchState((prev) => ({
                        ...prev,
                        category_seq: value ?? "all",
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
                  {modelsData.length} results found
                  <span className="text-gray-500 fs-6">↓</span>
                </h3>
              </div>
              {/*end::Title*/}
              {/*begin::Controls*/}
            </div>

            <div id="kt_project_users_table_pane">
              <MantineReactTable table={table} />
            </div>
          </div>
        </div>
        {/*end::Post*/}
      </div>
      {/*end::Container*/}
    </div>
  );
}
