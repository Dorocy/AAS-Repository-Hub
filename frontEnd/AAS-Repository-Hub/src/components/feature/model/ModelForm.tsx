/*
 * 파일명: src/app/aas/ins/page.tsx
 * 작성자: 김태훈
 * 작성일: 2024-03-15
 * 최종수정일: 2024-03-29
 *
 * 저작권: (c) 2025 IMPIX. 모든 권리 보유.
 *
 * 설명: AAS 템플릿 등록 페이지를 제공합니다.
 */
"use client";
import React, { useState, useEffect, useRef, useMemo } from "react";
import Link from "next/link";
import { confirmSave } from "@/utils/modal";
import toast from "react-hot-toast";
import { usePathname, useRouter } from "next/navigation";
import { Dropzone, FileWithPath } from "@mantine/dropzone";
import {
  deleteModel,
  exportModel,
  getCodeList,
  getModel,
  getModelVersions,
  importModel,
  upsertModel,
  verifyModel,
} from "@/api";
import {
  IconUpload,
  IconX,
  IconPhoto,
  IconTrash,
  IconMaximize,
  IconBrowserMaximize,
} from "@tabler/icons-react";
import _ from "lodash";
import {
  Button,
  FileButton,
  Group,
  Indicator,
  Text,
  Image,
  Menu,
  ActionIcon,
  Flex,
  Tooltip,
  Box,
  LoadingOverlay,
} from "@mantine/core";
import { canAccessPath, PROTECTED_ROUTES, ROUTES } from "@/constants/routes";
import { addValuePaths, parsingAAS, parsingSub } from "@/utils/aas";
import AASTree from "./AASTree";
import { base64ToFile } from "@/utils";
import CancelButton from "@/components/CancelButton";
import { useQuery } from "@tanstack/react-query";
import CustomCombobox from "@/components/CustomCombobox";
import { modals } from "@mantine/modals";
import AASTreeModal from "@/components/AASTreeModal";
import imageCompression from "browser-image-compression";
import { showToast } from "@/utils/toast";
import VerifyDetailView from "@/components/VerifyDetailView";
import { useAuth } from "@/contexts/AuthContext";
import { UserRole } from "@/constants/roles";
import CategoryCombobox from "@/components/CategoryCombobox";

type Mode = "create" | "edit" | "view";

interface ModelFormProps {
  mode: Mode;
  model?: Record<string, any>;
  modelType: "aasmodel" | "submodel";
  modalMode?: boolean;
}

export default function ModelForm({
  mode,
  model,
  modelType,
  modalMode = false,
}: ModelFormProps) {
  const routeKey = modelType.toUpperCase() as "AASMODEL" | "SUBMODEL";
  const router = useRouter();

  const { user } = useAuth();

  useEffect(() => {
    // document.title = "AAS 템플릿 등록";
  }, []);

  //   카테고리 목록 조회
  const { data: categorys, isSuccess: isSuccessCategorys } = useQuery({
    queryKey: ["common/code", "category"],
    queryFn: () => getCodeList("category"),
  });

  const { data: versions = [] } = useQuery({
    queryKey: [`${modelType}_seq`, mode],
    queryFn: () =>
      getModelVersions({
        modelType,
        modelSeq: model?.[`${modelType}_seq`],
      }),
    enabled: ["edit", "view"].includes(mode),
  });

  const [state, setState] = useState({
    [`${modelType}_name`]: "",
    description: "",
    category_seq: "",
  });

  const [model_img, setModel_img] = useState();

  const [modelFile, setModelFile] = useState<any>();
  const [metadata, setMetaData] = useState<any>();
  const [loading, setLoading] = useState<boolean>(false);

  // const [treeData, setTreeData] = useState<any[] | null>(null);

  const modelRef = useRef<any>({});
  const treeDataRef = useRef<any>({});
  const resetRef = useRef<() => void>(null);

  const verificationRef = useRef<() => void>(null);
  const [verificationActive, setVerificationActive] = useState<any>();

  const previewThumbnail = useMemo(() => {
    if (!model_img) return null;
    const imageUrl = URL.createObjectURL(model_img);
    return (
      <Image src={imageUrl} onLoad={() => URL.revokeObjectURL(imageUrl)} />
    );
  }, [model_img]);

  const setModelData = (model) => {
    if (model == null) return;
    const {
      description,
      category_seq,
      metadata,
      [`${modelType}_img`]: model_img,
      filename,
      mime_type,
      ...rest
    } = model;
    modelRef.current = { ...rest };

    setState({
      [`${modelType}_name`]: model[`${modelType}_name`] || "",
      description: description || "",
      category_seq: String(category_seq),
    });

    if (model_img) {
      const image = base64ToFile(model_img, filename, mime_type);
      setModel_img(image);
    }

    if (metadata) {
      const parsedData =
        typeof metadata == "object" ? metadata : JSON.parse(metadata);
      setMetaData(parsedData);
      // const tree =
      //   modelType == "aasmodel"
      //     ? parsingAAS(addValuePaths({ ...parsedData }))
      //     : parsingSub(addValuePaths({ ...parsedData }));

      // setTreeData(Array.isArray(tree) ? tree : [tree]);
    }
  };

  const treeData = useMemo(() => {
    if (!metadata) {
      return;
    }
    const tree =
      modelType == "aasmodel"
        ? parsingAAS(addValuePaths({ ...metadata }))
        : parsingSub(addValuePaths({ ...metadata }));
    return Array.isArray(tree) ? tree : [tree];
  }, [metadata]);

  const version = versions.find((v) => v.id == model?.[`${modelType}_seq`]);

  useEffect(() => {
    if (version) {
      showToast.success(`${version.text} Version loaded successfully`);
    }
    setModelData(model);
  }, [model]);

  //  배포 아이디
  const publishKey =
    modelType == "aasmodel"
      ? `${modelType}_template_id`
      : `${modelType}_semantic_id`;

  const clearFile = () => {
    setMetaData(null);
    verificationRef.current = null;
    setVerificationActive(null);
    resetRef.current?.();
  };

  const onChangeImport = async (file: File | null) => {
    if (!file) return;
    try {
      setModelFile(file);
      const modelId =
        mode == "edit" ? modelRef.current[`${modelType}_id`] : undefined;
      let result;
      result = await importModel({ modelType, file, modelId });
      if (!result) return;

      const metadata = typeof result === "string" ? JSON.parse(result) : result;

      setMetaData(metadata);

      verificationRef.current = null;
      setVerificationActive(null);
    } catch (error: any) {
      console.error(error.message);
    } finally {
      resetRef.current?.();
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setState((prev) => ({
      ...prev,
      [e.target.id]: e.target.value,
    }));
  };

  const getModelId = (metadata: object) => {
    if (mode == "create") {
      if (metadata == null) {
        return "";
      }
      if (modelType === "aasmodel") {
        return metadata["assetAdministrationShells"][0].id;
      } else {
        return metadata["id"];
      }
    } else {
      return modelRef.current[`${modelType}_id`];
    }
  };

  const handleSubmit = async (status: "temporary" | "draft") => {
    if (!(await confirmSave("Do you want to Save?"))) return;

    if (mode == "edit") {
      const { data: existSeq } = await verifyModel({
        modelType,
        modelId: modelRef.current?.[`${modelType}_id`],
        errorThrow: false,
      });

      if (
        existSeq != undefined &&
        existSeq != "" &&
        existSeq != modelRef.current?.[`${modelType}_seq`]
      ) {
        const isConfirm = await confirmSave(
          `Model already updated in sequence ${existSeq}. Do you want to continue and overwrite your changes?`,
          {
            labels: {
              confirm: "Confirm",
              cancel: "Cancel",
            },
          }
        );
        if (!isConfirm) return;
      }
    }

    // 유효성 검사
    // 모델명, 설명,
    if (state[`${modelType}_name`] == "") {
      return toast("Enter Template name", {
        icon: "⚠️",
      });
    }
    if (state.description == "") {
      return toast("Enter description", {
        icon: "⚠️",
      });
    }
    if (state.category_seq == null || state.category_seq == "") {
      return toast("Select category", {
        icon: "⚠️",
      });
    }

    if (metadata == null) {
      return toast(`Import ${routeKey}`, {
        icon: "⚠️",
      });
    }

    const payloadMetadata = Array.isArray(metadata)
      ? [...metadata]
      : { ...metadata };
    for (const key in treeDataRef.current) {
      const value = treeDataRef.current[key];
      _.set(payloadMetadata, key, value);
    }

    let body = {};

    if (mode == "create") {
      body = {
        [`${modelType}_seq`]: "",
        [`${modelType}_id`]: getModelId(payloadMetadata),
        [publishKey]: "",
        [modelType == "aasmodel" ? "version" : `${modelType}_version`]: "",
        type: "",
        status: "",
        source_project: "",
      };
    } else {
      body = {
        ...modelRef.current,
      };
    }

    body = {
      ...body,
      [`${modelType}_name`]: state[`${modelType}_name`],
      description: state.description,
      category_seq: state.category_seq,
      metadata: JSON.stringify(payloadMetadata),
    };

    if (["published", "deprecated"].includes(modelRef.current.status)) {
      body[`${modelType}_seq`] = "";
    }

    if (modelType == "submodel") {
      body[publishKey] = payloadMetadata.semanticId.keys[0].value;
    }

    const payload = {
      body: JSON.stringify(body),
    };

    if (model_img) {
      const compressed = await imageCompression(model_img, {
        maxWidthOrHeight: 256,
        useWebWorker: true,
        maxSizeMB: 0.1,
      });
      const image = new File([compressed], compressed.name, {
        type: compressed.type,
      });
      payload["image"] = image as File;
    }

    if (modelFile) {
      payload["attachments"] = modelFile;
    }

    const formData = new FormData();
    Object.entries(payload).forEach(([key, value]) => {
      formData.append(key, value);
    });

    try {
      setLoading(true);
      const modelSeq = await upsertModel({
        modelType,
        status,
        formData,
        errorThrow: true,
        withToast: true,
      });
      router.push(ROUTES[routeKey].VIEW(modelSeq));
    } catch (error) {
      console.log(error);
      let json = error?.cause?.json;

      if (json) {
        // 여기서 검증 데이터 저장
        verificationRef.current = JSON.parse(error?.cause?.json.data);
        // 검증 active id 는 실패한 첫 번째 요소로 저장
        // const [verificationKey] = Object.entries(
        //   verificationRef.current
        // ).find(([_, obj]) => obj.count > 0);
        // setVerificationActive(verificationKey);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format, model) => {
    exportModel({
      modelType,
      format,
      modelSeq: model[`${modelType}_seq`],
      filename: model[`${modelType}_name`],
    });
  };

  const renderFootButtons = () => {
    const modelSeq = model?.[`${modelType}_seq`];
    const aasEditLink = ROUTES[routeKey].EDIT(modelSeq);
    const instanceLink = `${ROUTES.INSTANCE.CREATE}?modelSeq=${modelSeq}`;
    switch (mode) {
      case "view":
        return (
          <>
            {user?.user_group_seq <= UserRole.Approvedor && (
              <Link
                href={aasEditLink}
                className="btn btn-light-success btn-sm me-2"
              >
                <i className="fa-regular fa-pen-to-square"></i> Edit{" "}
              </Link>
            )}
            {user != null && (
              <Menu shadow="md" width={200}>
                <Menu.Target>
                  <button className="btn btn-success btn-sm me-2 dropdown-toggle">
                    Export
                  </button>
                </Menu.Target>
                <Menu.Dropdown>
                  {(modelType == "aasmodel"
                    ? ["json", "xml", "aasx"]
                    : ["json"]
                  ).map((format) => (
                    <Menu.Item
                      key={format}
                      onClick={() => handleExport(format, model)}
                    >
                      {format}
                    </Menu.Item>
                  ))}
                </Menu.Dropdown>
              </Menu>
            )}
            {user != null &&
              modelType == "aasmodel" &&
              model?.status == "published" && (
                <Link href={instanceLink} className="btn btn-success btn-sm">
                  <i className="fa-regular fa-copy"></i> Instance{" "}
                </Link>
              )}
          </>
        );
      case "create":
      case "edit":
        return (
          <>
            <CancelButton />
            {["temporary", "draft"].includes(model?.status) && (
              <button
                type="button"
                className="btn btn-danger btn-sm me-2"
                disabled={loading}
                onClick={async () => {
                  const isConfirm = await confirmSave(
                    "Are you sure you want to delete it?",
                    {
                      labels: { confirm: "Delete", cancel: "Cancel" },
                      confirmProps: { color: "red.8" },
                    }
                  );
                  if (isConfirm) {
                    const result = await deleteModel({
                      modelType,
                      modelSeq: modelSeq,
                    });

                    router.replace(ROUTES[routeKey].LIST);
                  }
                }}
              >
                <i className="fa-solid fa-cloud"></i> Delete
              </button>
            )}
            {model?.status != "draft" && (
              <button
                type="button"
                className="btn btn-light-success btn-sm me-2"
                disabled={loading}
                onClick={() => handleSubmit("temporary")}
              >
                <i className="fa-solid fa-cloud"></i> Temporarily save{" "}
              </button>
            )}
            <button
              type="button"
              className="btn btn-success btn-sm me-2"
              disabled={loading}
              onClick={() => handleSubmit("draft")}
            >
              <i className="fa-solid fa-upload"></i>{" "}
              {model?.status == null || model?.status == "published"
                ? "Register"
                : "Save"}
            </button>
          </>
        );
      default:
        break;
    }
  };

  const handleOpen = () => {
    if (!verificationActive) return;
    modals.open({
      withCloseButton: false,
      fullScreen: true,
      closeOnEscape: false,
      children: (
        <>
          <Flex
            justify="flex-end"
            style={{ position: "sticky", top: 10, zIndex: 10 }}
          >
            <Button
              onClick={() => {
                modals.closeAll();
              }}
            >
              Close
            </Button>
          </Flex>
          <div className="text-muted fw-semibold fs-5">
            {Array.isArray(
              verificationRef.current?.[verificationActive]?.message
            ) &&
              verificationRef.current?.[verificationActive]?.message.map(
                (msg) => (
                  <>
                    {msg}
                    <br />
                  </>
                )
              )}
          </div>
        </>
      ),
    });
  };

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
              {modelType?.toUpperCase()} -{" "}
              {mode == "create" ? "Register" : mode == "edit" ? "Edit" : "View"}
            </h1>
            {/* end::Title */}
            {/* begin::Breadcrumb */}
            <ul className="breadcrumb breadcrumb-dot fw-semibold text-gray-600 fs-7 my-1">
              {/* begin::Item */}
              <li className="breadcrumb-item text-gray-600">
                <a href="index" className="text-gray-600 text-hover-primary">
                  Home
                </a>
              </li>
              {/* end::Item */}
              {/* begin::Item */}
              <li className="breadcrumb-item text-gray-600">
                {modelType?.toUpperCase()} -{" "}
                {mode == "create"
                  ? "Register"
                  : mode == "edit"
                    ? "Edit"
                    : "View"}
              </li>
              {/* end::Item */}
            </ul>
            {/* end::Breadcrumb */}
          </div>
          {/* end::Page title */}
          {/* begin::Actions */}
          <div className="d-flex align-items-center py-2 py-md-1">
            {!modalMode && mode == "view" && (
              <div className="form-floating">
                <select
                  id="version"
                  className="form-select  form-select-md fw-semibold me-3"
                  value={model?.[`${modelType}_seq`]}
                  onChange={(e) => {
                    router.push(ROUTES[routeKey].VIEW(e.target.value));
                  }}
                >
                  {versions.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.text}
                    </option>
                  ))}
                </select>
                <label htmlFor="version">Version</label>
              </div>
            )}
            {!modalMode && (
              <Link
                href={ROUTES[routeKey].LIST}
                className="btn btn-lightactive"
              >
                <i className="fa-solid fa-list"></i> List
              </Link>
            )}
            {["create", "edit"].includes(mode) && (
              <>
                {" "}
                <FileButton
                  resetRef={resetRef}
                  onChange={onChangeImport}
                  accept=".aasx,.xml,.json,application/xml,text/xml,application/json"
                >
                  {(props) => (
                    <button
                      className="btn btn-success me-3 fw-bold "
                      {...props}
                    >
                      <i className="fa-solid fa-file-import"></i> Import
                    </button>
                  )}
                </FileButton>
                {mode === "create" && (
                  <button
                    disabled={!metadata}
                    className={`btn btn-${!!metadata ? "danger" : ""} fw-bold`}
                    onClick={clearFile}
                  >
                    <i className="fa-regular fa-file-circle-minus"></i> Reset
                  </button>
                )}
              </>
            )}
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
          <div className="card">
            <div className="card-header">
              {/* begin::Card title */}
              <div className="card-title fs-3 fw-bold text-primary">
                {mode == "create" ? "Register" : model?.[`${modelType}_name`]}
              </div>
              {/* end::Card title */}
            </div>

            <div id="" className="collapse show p-9">
              <div className="card">
                <div
                  className="card-header border-0 bg-light"
                  style={{ minHeight: "50px" }}
                >
                  {/* begin::Card title */}
                  <div className="card-title fs-4 fw-bold">
                    Template info
                    {version != null && (
                      <span className="badge badge-light-success mx-2">
                        {`Version ${version.text}`}
                      </span>
                    )}
                  </div>
                  {/* end::Card title */}
                </div>
                <div id="" className="collapse show">
                  {/* begin::Form */}
                  <form id="kt_account_profile_details_form" className="form">
                    {/* begin::Card body */}
                    <div className="card-body border-top p-9">
                      {["view", "edit"].includes(mode) && (
                        <div className="row mb-6">
                          <label className="col-lg-4 col-form-label fw-semibold fs-6">
                            Status
                          </label>
                          <div className="col-lg-8 fv-row">
                            <label className="col-form-label fw-semibold fs-6">
                              {model?.status}
                            </label>
                          </div>
                        </div>
                      )}
                      {["view", "edit"].includes(mode) && (
                        <div className="row mb-6">
                          <label className="col-lg-4 col-form-label fw-semibold fs-6">
                            Sequence
                          </label>
                          <div className="col-lg-8 fv-row">
                            <label className="col-form-label fw-semibold fs-6">
                              {model?.[`${modelType}_seq`]}
                            </label>
                          </div>
                        </div>
                      )}
                      {["view", "edit"].includes(mode) && (
                        <div className="row mb-6">
                          <label className="col-lg-4 col-form-label fw-semibold fs-6">
                            {modelType == "aasmodel"
                              ? "Template ID"
                              : "Semantic ID"}
                          </label>
                          <div className="col-lg-8 fv-row">
                            <label className="col-form-label fw-semibold fs-6">
                              {model?.[publishKey]}
                            </label>
                          </div>
                        </div>
                      )}
                      <div className="row mb-6">
                        <label className="col-lg-4 col-form-label fw-semibold fs-6">
                          Template name
                        </label>
                        <div className="col-lg-8 fv-row">
                          {mode == "view" ? (
                            <label className="col-form-label fw-semibold fs-6">
                              {model?.[`${modelType}_name`]}
                            </label>
                          ) : (
                            <input
                              type="text"
                              id={`${modelType}_name`}
                              className="form-control form-control-lg"
                              placeholder="Please enter"
                              value={state[`${modelType}_name`]}
                              onChange={handleInputChange}
                            />
                          )}
                        </div>
                      </div>

                      <div className="row mb-6">
                        <label className="col-lg-4 col-form-label fw-semibold fs-6">
                          Description
                        </label>
                        <div className="col-lg-8 fv-row">
                          {mode == "view" ? (
                            <label className="col-form-label fw-semibold fs-6">
                              {model?.description}
                            </label>
                          ) : (
                            <input
                              type="text"
                              id="description"
                              className="form-control form-control-lg"
                              placeholder="Please enter"
                              value={state.description}
                              onChange={handleInputChange}
                            />
                          )}
                        </div>
                      </div>

                      <div className="row mb-6">
                        <label className="col-lg-4 col-form-label fw-semibold fs-6">
                          Category
                        </label>
                        <div className="col-lg-8 fv-row">
                          {mode == "view" ||
                          model?.[`${modelType}_template_id`] ? (
                            <label className="col-form-label fw-semibold fs-6">
                              {model?.category_name}
                            </label>
                          ) : (
                            <CategoryCombobox
                              selectLeafOnly
                              value={state.category_seq ?? ""}
                              setValue={(value) =>
                                setState({ ...state, category_seq: value })
                              }
                            />
                          )}
                        </div>
                      </div>

                      <div className="row">
                        <label className="col-lg-4 col-form-label fw-semibold fs-6">
                          Model Id
                        </label>
                        <div className="col-lg-8 fv-row">
                          <label className="col-form-label fw-semibold fs-6">
                            {mode == "create"
                              ? getModelId(metadata)
                              : modelRef.current[`${modelType}_id`]}
                          </label>
                        </div>
                      </div>
                    </div>
                  </form>
                  {/* end::Form */}
                </div>
              </div>
              {mode != "view" ? (
                <div className="card mt-10">
                  <div
                    className="card-header border-0 bg-light"
                    style={{ minHeight: "50px" }}
                  >
                    {/* begin::Card title */}
                    <div className="card-title fs-4 fw-bold">
                      Thumbnail image
                    </div>
                    {/* end::Card title */}
                  </div>
                  <div id="" className="collapse show">
                    {/* begin::Form */}
                    <form id="kt_account_profile_details_form" className="form">
                      {/* begin::Card body */}
                      <div className="card-body border-top p-9">
                        <div className="row">
                          <label className="col-lg-4 col-form-label fw-semibold fs-6">
                            Thumbnail (256px x 256px)
                          </label>
                          <div className="col-lg-8">
                            {/* begin::Image input */}
                            <div style={{ height: "225px" }}>
                              {/* begin::Preview existing avatar */}
                              {mode == "view" ? (
                                <div
                                  style={{ width: "125px", height: "125px" }}
                                >
                                  {previewThumbnail}
                                </div>
                              ) : (
                                <Indicator
                                  id="indicater"
                                  color="red"
                                  label={
                                    <IconTrash
                                      onClick={(e) => {
                                        setModel_img(undefined);
                                      }}
                                    />
                                  }
                                  inline
                                  offset={4}
                                  size={32}
                                  style={{
                                    cursor: "pointer",
                                  }}
                                >
                                  <Dropzone
                                    multiple={false}
                                    onDrop={(files) => {
                                      setModel_img(files[0]);
                                    }}
                                    onReject={(files) =>
                                      console.log("rejected files", files)
                                    }
                                    accept={[
                                      "image/png",
                                      "image/jpg",
                                      "image/jpeg",
                                    ]}
                                    w={256}
                                    h={256}
                                  >
                                    <Group
                                      justify="center"
                                      gap="xl"
                                      mih={220}
                                      style={{ pointerEvents: "none" }}
                                    >
                                      {previewThumbnail ? (
                                        previewThumbnail
                                      ) : (
                                        <>
                                          <Dropzone.Accept>
                                            <IconUpload
                                              size={52}
                                              color="var(--mantine-color-blue-6)"
                                              stroke={1.5}
                                            />
                                          </Dropzone.Accept>
                                          <Dropzone.Reject>
                                            <IconX
                                              size={52}
                                              color="var(--mantine-color-red-6)"
                                              stroke={1.5}
                                            />
                                          </Dropzone.Reject>
                                          <Dropzone.Idle>
                                            <IconPhoto
                                              size={52}
                                              color="var(--mantine-color-dimmed)"
                                              stroke={1.5}
                                            />
                                          </Dropzone.Idle>
                                        </>
                                      )}
                                      <div>
                                        <Text
                                          size="sm"
                                          c="dimmed"
                                          inline
                                          mt={7}
                                        >
                                          Allowed file types: png, jpg, jpeg
                                        </Text>
                                      </div>
                                    </Group>
                                  </Dropzone>
                                </Indicator>
                              )}
                              {/* end::Preview existing avatar */}
                              {/* begin::Label */}

                              {/* end::Hint */}
                            </div>
                          </div>
                        </div>
                      </div>
                    </form>
                    {/* end::Form */}
                  </div>
                </div>
              ) : (
                ""
              )}
              <div className="card mt-10">
                <div
                  className="card-header border-0 bg-light"
                  style={{ minHeight: "50px" }}
                >
                  {/* begin::Card title */}
                  <div className="card-title fs-4 fw-bold">
                    <AASTreeModal
                      treeData={treeData}
                      treeDataRefCurrent={treeDataRef.current}
                      metadata={metadata}
                      setMetaData={setMetaData}
                      mode={mode}
                    />
                    Model
                    {Array.isArray(treeData) && (
                      <span className="badge badge-light-success mx-2">
                        {treeData[0].id}
                      </span>
                    )}
                  </div>
                  {/* end::Card title */}
                </div>
                <div id="" className="collapse show">
                  {/* begin::Form */}
                  <form id="kt_account_profile_details_form" className="form">
                    {/* begin::Card body */}
                    <div className="card-body border-top p-9">
                      {Array.isArray(treeData) && (
                        <AASTree
                          style={{ maxHeight: "80vh", overflow: "scroll" }}
                          mb={"sm"}
                          data={treeData}
                          treeDataRefCurrent={treeDataRef.current}
                          editMode={["create", "edit"].includes(mode)}
                        />
                      )}
                    </div>
                  </form>
                  {/* end::Form */}
                </div>
              </div>

              <VerifyDetailView
                verificationRef={verificationRef}
                verificationActive={verificationActive}
                setVerificationActive={setVerificationActive}
              />
            </div>

            {!modalMode && (
              <div className="card-footer d-flex justify-content-end py-6 px-9">
                {renderFootButtons()}
              </div>
            )}
          </div>
        </div>
        {/* end::Post */}
      </div>
      {/* end::Container */}
    </>
  );
}
