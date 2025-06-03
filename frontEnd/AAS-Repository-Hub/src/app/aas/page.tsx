/*
 * 파일명: src/pages/aas/index.tsx
 * 작성자: 김태훈
 * 작성일: 2024-03-15
 * 최종수정일: 2024-03-29
 *
 * 저작권: (c) 2025 IMPIX. 모든 권리 보유.
 *
 * 설명: AAS 템플릿 목록 페이지를 제공합니다.
 */

"use client";

import { exportModel, getCodeList, getModelList, verifyModel } from "@/api";
import CustomCombobox from "@/components/CustomCombobox";
import ModelCard from "@/components/feature/model/ModelCard";
import FlexTable from "@/components/FlexTable";
import SearchBox from "@/components/SearchBox";
import { UserRole } from "@/constants/roles";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/contexts/AuthContext";
import { getCodeTree } from "@/utils";
import { confirmSave } from "@/utils/modal";
import {
  Badge,
  Flex,
  Anchor,
  Button,
  Menu,
  Text,
  Tree,
  Box,
  Group,
  useTree,
  Combobox,
  Input,
  InputBase,
  useCombobox,
} from "@mantine/core";
import {
  IconChevronDown,
  IconCurrencyLeu,
  IconSquareRoundedMinus,
  IconSquareRoundedPlus,
} from "@tabler/icons-react";
import { useQuery } from "@tanstack/react-query";
import {
  MRT_PaginationState,
  MRT_RowData,
  useMantineReactTable,
} from "mantine-react-table";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import React, { useState, useEffect, useRef, useMemo, ReactNode } from "react";
import toast from "react-hot-toast";
import mantineTreeClasses from "@/css/MantineTree.module.css";
import CategoryCombobox from "@/components/CategoryCombobox";

// export const metadata = { title: "AAS 템플릿 목록" };

interface AASTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  lastUpdated: string;
  status: string;
}

export default function Page() {
  const router = useRouter();
  const { user } = useAuth();
  const codeTree = useTree();

  const searchParams = useSearchParams();
  const title = searchParams.get("title");
  const titleRef = useRef(title);

  useEffect(() => {
    document.title = "AAS 템플릿 목록";
  }, []);
  const modelType = "aasmodel";

  // 검색 박스 상태 값
  const [searchState, setSearchState] = useState({
    category_seq: "",
    searchKey: title ?? "",
  });

  // enter or click button
  const searchRef = useRef({
    searchKey: title ?? "",
  });

  const [layoutType, setLayoutType] = useState<"flex" | "table">("flex");
  const [pagination, setPagination] = useState<MRT_PaginationState>({
    pageIndex: 0,
    pageSize: 8,
  });

  const { data: categorys } = useQuery({
    queryKey: ["common/code"],
    queryFn: () => getCodeList("category"),
  });

  const {
    data: models,
    isFetching: isFetchingModels,
    isSuccess,
    refetch,
  } = useQuery({
    queryKey: [modelType, pagination, searchState],
    queryFn: () =>
      getModelList({
        modelType,
        pageNumber: pagination.pageIndex + 1,
        pageSize: pagination.pageSize,
        searchParams: {
          ...searchState,
          ...(titleRef.current != null ? { title: titleRef.current } : {}),
          p: "p",
        },
      }),
  });

  const modelsData = models?.data ?? [];

  // title 초기화
  useEffect(() => {
    titleRef.current = null;
  }, []);

  const handleExport = (format, model) => {
    exportModel({
      modelType,
      format,
      modelSeq: model[`${modelType}_seq`],
      filename: model[`${modelType}_name`],
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

  const renderGridItem = (model: any, i: number) => {
    return (
      <ModelCard
        key={model[`${modelType}_seq`] ?? i}
        model={model}
        modelType={modelType}
        i={i}
      />
    );
  };

  const table = useMantineReactTable({
    columns: [
      {
        accessorKey: "status",
        header: "Status",
        size: 135,
        Cell: ({ row }) => (
          <Badge
            mt={4}
            mr={4}
            color={
              row.original.status === "temporary"
                ? "blue"
                : row.original.status === "draft"
                  ? "red.4"
                  : row.original.status === "published"
                    ? "green"
                    : "dark.1"
            }
            radius="sm"
          >
            {row.original.status_nm}
          </Badge>
        ),
      },
      {
        accessorKey: `${modelType}_name`,
        header: "TEMPLATE NAME",
        Cell: ({ row }) => (
          <Flex align="center" gap="md">
            <Anchor
              onClick={(e) => {
                e.preventDefault();
                user != null &&
                  router.push(
                    ROUTES[modelType.toUpperCase()].VIEW(
                      row.original[`${modelType}_seq`]
                    )
                  );
              }}
            >
              <Text>{row.original[`${modelType}_name`]}</Text>
            </Anchor>
          </Flex>
        ),
      },
      { accessorKey: "description", header: "description" },
      { accessorKey: "category_name", header: "CATEGORY" },
      { accessorKey: `${modelType}_template_id`, header: "TEMPLATE ID" },
      {
        accessorKey: "externalButtons",
        header: "",
        size: 145,
        Cell: ({ row }) => (
          <Flex align={"center"} gap={"xs"}>
            {user != null && user?.user_group_seq <= UserRole.Approvedor && (
              <button
                // href={ROUTES.AASMODEL.EDIT(row.original[`${modelType}_seq`])}
                className="btn btn-light-success btn-sm"
                onClick={async () => {
                  const { data: existSeq } = await verifyModel({
                    modelType,
                    modelId: row.original[`${modelType}_id`],
                    errorThrow: false,
                  });
                  if (
                    existSeq != undefined &&
                    existSeq != "" &&
                    existSeq != row.original[`${modelType}_seq`]
                  ) {
                    const isConfirm = await confirmSave(
                      `This model is already being edited in sequence ${existSeq}. Would you like to continue with that task?`,
                      {
                        labels: {
                          confirm: "Confirm",
                          cancel: "Cancel",
                        },
                      }
                    );
                    if (isConfirm) {
                      router.push(
                        ROUTES[modelType.toUpperCase()].EDIT(existSeq)
                      );
                    }
                  } else {
                    router.push(
                      ROUTES[modelType.toUpperCase()].EDIT(
                        row.original[`${modelType}_seq`]
                      )
                    );
                  }
                }}
              >
                <i className="fa-regular fa-pen-to-square"></i> Edit
              </button>
            )}
            {user != null && (
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
            )}
          </Flex>
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
      columnPinning: {
        // right: ["externalButtons"],
      },
    },
    layoutMode: "grid",
    onPaginationChange: setPagination,
  });

  return (
    <>
      {/* begin::Toolbar */}
      <div className="toolbar py-5 py-lg-5" id="kt_toolbar">
        {/* begin::Container */}
        <div
          id="kt_toolbar_container"
          className="container-xxl d-flex flex-stack flex-wrap"
        >
          {/* begin::Page title */}
          <div className="page-title d-flex flex-column me-3">
            {/* begin::Title */}
            <h1 className="d-flex text-gray-900 fw-bold my-1 fs-3">
              AAS Template
            </h1>
            {/* end::Title */}
            {/* begin::Breadcrumb */}
            <ul className="breadcrumb breadcrumb-dot fw-semibold text-gray-600 fs-7 my-1">
              {/* begin::Item */}
              <li className="breadcrumb-item text-gray-600">
                <Link href="/" className="text-gray-600 text-hover-primary">
                  Home
                </Link>
              </li>
              {/* end::Item */}
              {/* begin::Item */}
              <li className="breadcrumb-item text-gray-600">AAS Template</li>
              {/* end::Item */}
            </ul>
            {/* end::Breadcrumb */}
          </div>
          {/* end::Page title */}
          {/* begin::Actions */}
          <div className="d-flex align-items-center py-2 py-md-1">
            {/* begin::Button */}
            {user != null && user?.user_group_seq <= UserRole.Approvedor && (
              <Link
                href={ROUTES.AASMODEL.CREATE}
                className="btn btn-success fw-bold"
              >
                <i className="fa-solid fa-tablet"></i> Register
              </Link>
            )}
            {/* end::Button */}
          </div>
          {/* end::Actions */}
        </div>
        {/* end::Container */}
      </div>
      {/* end::Toolbar */}
      {/* begin::Container */}
      <div
        id="kt_content_container"
        className="d-flex flex-column-fluid align-items-start container-xxl"
      >
        {/* begin::Post */}
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
                    defaultValue={searchRef.current.searchKey ?? ""}
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
        {/* end::Post */}
      </div>
      {/* end::Container */}
    </>
  );
}
