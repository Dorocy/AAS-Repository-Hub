/*
 * 파일명: src/app/distribute/page.tsx
 * 작성자: 김태훈
 * 작성일: 2024-03-15
 * 최종수정일: 2024-03-29
 *
 * 저작권: (c) 2025 IMPIX. 모든 권리 보유.
 *
 * 설명: AAS 템플릿 배포 관리 페이지를 제공합니다.
 */

"use client";

import { getCodeList, getPublishedList } from "@/api";
import CategoryCombobox from "@/components/CategoryCombobox";
import CustomCombobox from "@/components/CustomCombobox";
import DistributeCard from "@/components/feature/distribute/DistributeCard";
import FlexTable from "@/components/FlexTable";
import SearchBox from "@/components/SearchBox";
import { ROUTES } from "@/constants/routes";
import { formatDateToDotYMD } from "@/utils";
import { Flex, Avatar, Anchor, Button, Text } from "@mantine/core";
import { IconList } from "@tabler/icons-react";
import { useQuery } from "@tanstack/react-query";
import {
  MRT_PaginationState,
  useMantineReactTable,
  MRT_RowData,
} from "mantine-react-table";
import Link from "next/link";
import router from "next/router";
import { type } from "os";
import React, { useRef, useState } from "react";

export default function Page() {
  // 검색 박스 상태 값
  const [searchState, setSearchState] = useState({
    status: "all",
    ty: "all",
    category_seq: "",
    searchKey: "",
  });

  // enter or click button
  const searchRef = useRef({
    searchKey: "",
  });

  const [layoutType, setLayoutType] = useState<"flex" | "table">("flex");
  const [pagination, setPagination] = useState<MRT_PaginationState>({
    pageIndex: 0,
    pageSize: 8,
  });

  //   상태 조회
  const { data: statusList, isSuccess: isSuccessStatusList } = useQuery({
    queryKey: ["common/code", "SYS100"],
    queryFn: () => getCodeList("SYS100"),
  });

  //   모델 타입 조회
  const { data: modelTypes, isSuccess: isSuccessModelTypes } = useQuery({
    queryKey: ["common/code", "SYS200"],
    queryFn: () => getCodeList("SYS200"),
  });

  // 카테고리 조회
  const { data: categorys } = useQuery({
    queryKey: ["common/code"],
    queryFn: () => getCodeList("category"),
  });

  const {
    data: models,
    isFetching: isFetchingModels,
    refetch,
  } = useQuery({
    queryKey: [type, pagination, searchState],
    queryFn: () =>
      getPublishedList({
        status: searchState.status,
        type: searchState.ty,
        pageNumber: pagination.pageIndex + 1,
        pageSize: pagination.pageSize,
        searchParams: {
          category_seq: searchState.category_seq,
          searchKey: searchState.searchKey,
          p: "p",
        },
      }),
  });

  const modelsData = models?.data ?? [];

  const renderGridItem = (model: any, i: number) => {
    return (
      model.target_seq != null && (
        <DistributeCard
          key={`${model.target_seq}${model.ty}`}
          model={model}
          i={i}
        />
      )
    );
  };

  const table = useMantineReactTable({
    columns: [
      {
        accessorKey: "ty",
        header: "Model Type",
        size: 80,
        Cell: ({ cell }) => {
          return (
            <span
              className={`badge badge-light${cell.getValue() == "aasmodel" ? "-primary" : ""}  bage_body`}
            >
              {cell.getValue() == "aasmodel" ? "AAS" : "Submodel"}
            </span>
          );
        },
      },
      {
        accessorKey: "target_name",
        header: "Template Name",
        Cell: ({ row }) => {
          return (
            <Flex align="center" gap="md">
              <Avatar size={"sm"} color="dark">
                <IconList size={18} />
              </Avatar>
              <Anchor
                href={ROUTES.DISTRIBUTE.VIEW({
                  modelType: row.original.ty,
                  targetSeq: row.original.target_seq,
                })}
                component={Link}
                underline="never"
              >
                <Text>{row.original[`target_name`]}</Text>
              </Anchor>
            </Flex>
          );
        },
      },
      {
        accessorKey: `target_version`,
        header: "Version",
        size: 80,
        Cell: ({ row }) =>
          row.original["target_version"] && (
            <Text>v{row.original["target_version"]}</Text>
          ),
      },
      {
        accessorKey: "status",
        header: "isPublished",
        size: 120,
        Cell: ({ row }) => <Text>{row.original["status_nm"]}</Text>,
      },
      {
        accessorKey: "tmp_seman_id",
        header: "Template_Id",
        size: 120,
        Cell: ({ row }) => <Text>{row.original["tmp_seman_id"]}</Text>,
      },
      {
        accessorKey: "create_date",
        header: "Published Date",
        size: 80,
        Cell: ({ row }) => {
          return formatDateToDotYMD(row.original["create_date"]);
        },
      },
      {
        accessorKey: "externalButtons",
        header: "",
        size: 75,
        Cell: ({ row }) => (
          <Link
            href={ROUTES.DISTRIBUTE.EDIT({
              modelType: row.original.ty,
              targetSeq: row.original.target_seq,
            })}
            className="btn btn-light-success btn-sm"
          >
            <i className="fa-regular fa-pen-to-square"></i> Edit
          </Link>
        ),
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
      // columnPinning: {
      //   right: ["externalButtons"],
      // },
    },
    layoutMode: "grid",
    onPaginationChange: setPagination,
  });

  const handleSearch = () => {
    const keyword = searchRef.current.searchKey;

    if (searchState.searchKey === keyword) {
      refetch();
    } else {
      setSearchState((prev) => ({ ...prev, searchKey: keyword }));
    }
  };

  return (
    <div>
      {/* Toolbar */}
      <div className="toolbar py-5 py-lg-5" id="kt_toolbar">
        {/* Container */}
        <div
          id="kt_toolbar_container"
          className="container-xxl d-flex flex-stack flex-wrap"
        >
          {/* Page title */}
          <div className="page-title d-flex flex-column me-3">
            {/* Title */}
            <h1 className="d-flex text-gray-900 fw-bold my-1 fs-3">Publish</h1>
            {/* Breadcrumb */}
            <ul className="breadcrumb breadcrumb-dot fw-semibold text-gray-600 fs-7 my-1">
              {/* Item */}
              <li className="breadcrumb-item text-gray-600">
                <a href="/" className="text-gray-600 text-hover-primary">
                  Home
                </a>
              </li>
              {/* Item */}
              <li className="breadcrumb-item text-gray-600">Publish</li>
            </ul>
          </div>
          {/*end::Page title*/}
          {/*begin::Actions*/}
          <div className="d-flex align-items-center py-2 py-md-1">
            {/*begin::Button*/}
            <a href="/distribute/ins" className="btn btn-success fw-bold">
              <i className="fa-solid fa-tablet"></i>
              Register
            </a>
            {/*end::Button*/}
          </div>
          {/*end::Actions*/}
        </div>
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
                {/* 배포 구분 */}
                <div className="col-lg-2 d-flex align-items-center mb-lg-0">
                  <i className="ki-outline ki-element-11 fs-1 text-gray-500 me-1"></i>

                  <CustomCombobox
                    border={false}
                    className="form-control border-0 flex-grow-1"
                    data={[
                      { value: "all", label: "Publish All" },
                      { value: "published", label: "published" },
                      { value: "deprecated", label: "deprecated" },
                    ]}
                    // mappingFn={(item) => ({ value: item.id, label: item.text })}
                    value={searchState.status}
                    onChange={(value) =>
                      setSearchState((prev) => ({
                        ...prev,
                        status: value ?? "all",
                        searchKey: searchRef.current.searchKey,
                      }))
                    }
                  />
                </div>
                {/* 모델 구분 */}
                <div className="col-lg-2 d-flex align-items-center mb-lg-0">
                  <i className="ki-outline ki-element-11 fs-1 text-gray-500 me-1"></i>

                  <CustomCombobox
                    border={false}
                    className="form-control border-0 flex-grow-1"
                    data={
                      modelTypes
                        ? [{ id: "all", text: "Model All" }, ...modelTypes]
                        : modelTypes
                    }
                    mappingFn={(item) => ({ value: item.id, label: item.text })}
                    value={searchState.ty}
                    onChange={(value) =>
                      setSearchState((prev) => ({
                        ...prev,
                        ty: value ?? "all",
                        searchKey: searchRef.current.searchKey,
                      }))
                    }
                  />
                </div>
                {/* 카테고리 */}
                <div className="col-lg-2 d-flex align-items-center mb-lg-0">
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
            </div>

            <FlexTable
              layoutType={layoutType}
              setLayoutType={setLayoutType}
              renderGridItem={renderGridItem}
              table={table}
            />
          </div>
        </div>
        {/*end::Post*/}
      </div>
      {/*end::Container*/}
    </div>
  );
}
