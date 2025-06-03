"use client";
import React from "react";
import { TableCard } from "../../TableCard";
import { exportModel, verifyModel } from "@/api";
import { ROUTES } from "@/constants/routes";
import { Menu } from "@mantine/core";
import { confirmSave } from "@/utils/modal";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { UserRole } from "@/constants/roles";

interface ModelCardProps {
  model: Record<string, any>;
  i: number;
  modelType: "aasmodel" | "submodel";
}

function ModelCard({ model, i, modelType }: ModelCardProps) {
  const router = useRouter();
  const { user } = useAuth();

  const routeKey = modelType.toUpperCase() as keyof typeof ROUTES;

  const handleExport = (format, model) => {
    exportModel({
      modelType,
      format,
      modelSeq: model[`${modelType}_seq`],
      filename: model[`${modelType}_name`],
    });
  };

  const badgeClass =
    model.status === "temporary"
      ? "badge-light-danger"
      : model.status === "draft"
        ? "badge-light-success"
        : model.status === "published"
          ? "badge-light-primary"
          : "badge-light-dark";

  const thumbnail = model[`${modelType}_img`]
    ? `data:${model["mime_type"]};base64,${model[`${modelType}_img`]}`
    : "";

  const modelKey = modelType == "aasmodel" ? "version" : "submodel_version";
  return (
    <TableCard key={model[`${modelType}_seq`] ?? i}>
      <div style={{ textAlign: "center" }}>
        <div className={`badge bage_body ${badgeClass}`}>
          {model.status_nm} {model[modelKey] ? "v" + model[modelKey] : ""}
        </div>
      </div>
      <div className="card-body d-flex flex-center flex-column pt-12 p-9">
        <a
          style={{ cursor: "pointer" }}
          onClick={(e) => {
            e.preventDefault();
            user != null &&
              router.push(
                ROUTES[modelType.toUpperCase()].VIEW(model[`${modelType}_seq`])
              );
          }}
        >
          <div className="symbol symbol-70px mb-5">
            <img
              src={thumbnail || "/assets/media/thumbnail_placeholder.svg"}
              alt="Thumbnail"
            />
          </div>
        </a>
        <a
          style={{ cursor: "pointer" }}
          onClick={(e) => {
            e.preventDefault();
            user != null &&
              router.push(
                ROUTES[modelType.toUpperCase()].VIEW(model[`${modelType}_seq`])
              );
          }}
          className="fs-4 text-gray-800 text-hover-primary fw-bold mb-0"
        >
          {model[`${modelType}_name`]}
        </a>
        <div className="fw-semibold text-gray-500 mb-6">
          {model.category_name}
        </div>
        {user != null && (
          <div className="d-flex flex-center flex-wrap">
            <div className="border border-gray-300 border-dashed rounded min-w-80px py-3 px-4 mx-2 mb-3 d-flex gap-2">
              {user?.user_group_seq <= UserRole.Approvedor && (
                <button
                  className="btn btn-light-success btn-sm"
                  onClick={async () => {
                    const { data: existSeq } = await verifyModel({
                      modelType,
                      modelId: model[`${modelType}_id`],
                      errorThrow: false,
                    });

                    if (
                      existSeq != undefined &&
                      existSeq != "" &&
                      existSeq != model[`${modelType}_seq`]
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
                        router.push(ROUTES[routeKey].EDIT(existSeq));
                      }
                    } else {
                      router.push(
                        ROUTES[routeKey].EDIT(model[`${modelType}_seq`])
                      );
                    }
                  }}
                >
                  <i className="fa-regular fa-pen-to-square"></i> Edit
                </button>
              )}
              <div className="dropdown">
                <Menu shadow="md" width={200}>
                  <Menu.Target>
                    <button className="btn btn-success btn-sm dropdown-toggle">
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
              </div>
            </div>
          </div>
        )}
      </div>
    </TableCard>
  );
}

export default ModelCard;
