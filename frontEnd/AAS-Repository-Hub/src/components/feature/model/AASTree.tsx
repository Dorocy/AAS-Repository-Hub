"use client";
import React, { useMemo, useState, memo, useEffect } from "react";
import {
  Accordion,
  Badge,
  Box,
  Button,
  Card,
  Container,
  Flex,
  Group,
  JsonInput,
  List,
  Text,
  TextInput,
  ThemeIcon,
  Title,
  Tree,
  useTree,
  Highlight,
  getTreeExpandedState,
} from "@mantine/core";
import {
  IconSquareRoundedMinus,
  IconSquareRoundedPlus,
  IconCurrencyLeu,
} from "@tabler/icons-react";
import toast from "react-hot-toast";
import treeNodeClass from "@/css/treeNode.module.css";
import { showToast } from "@/utils/toast";

// RenderObject: 재귀적으로 객체 내부의 속성을 렌더링합니다.
// editMode가 true이면 TextInput으로 입력 가능, false이면 단순 Text로 보여줍니다.
const RenderObject = memo(
  ({
    obj,
    indent = 0,
    state,
    editMode,
  }: {
    obj: any;
    indent?: number;
    state: any;
    editMode: boolean;
  }) => {
    const [innerState, setInnerState] = useState(state);

    useEffect(() => {
      setInnerState({ ...state });
    }, [obj, state]);

    return (
      <div
        style={{
          paddingLeft: `calc(2rem * ${indent})`,
          whiteSpace: "pre-wrap",
        }}
      >
        {Object.entries(obj)
          .filter(
            ([k, v]) => k !== "children" && k !== "label" && k !== "valuePath"
          )
          .sort((a, b) => -1 * (typeof a[1]).localeCompare(typeof b[1]))
          .map(([key, value]) => {
            const parentKey = obj.valuePath ? obj.valuePath : obj.value;
            const stateKey = parentKey ? `${parentKey}.${key}` : key;
            let tempEditMode = editMode
              ? ![
                  "assetAdministrationShells[0].id",
                  "id",
                  "semanticId.keys[0].value",
                ].includes(stateKey) && key != "id"
              : false;

            return (
              <Group
                key={key}
                w={"100%"}
                py="4"
                justify="space-between"
                wrap="nowrap"
                gap="xl"
              >
                <div style={{ width: "100%" }}>
                  {Array.isArray(value) ? (
                    <div>
                      <Title
                        order={3}
                        mb={"4"}
                        style={{
                          backgroundColor: "#fefefe",
                          border: "1px solid #efefef",
                          borderRadius: "5px",
                          padding: "5px 15px",
                          color: "#333",
                        }}
                      >
                        <i
                          className="fa-regular fa-file-lines me-2"
                          style={{ color: "#ee8843" }}
                        ></i>{" "}
                        {key}
                      </Title>

                      {/* <Badge
                        className="fs-6"
                        color="blue"
                        variant="dot"
                        size="xl"
                        mb={4}
                        fw={600}
                      >
                        {key}
                      </Badge> */}
                      {value.map((item, index) => (
                        <div key={index}>
                          {typeof item === "object" ? (
                            <RenderObject
                              obj={item}
                              state={state}
                              indent={indent + 1}
                              editMode={tempEditMode}
                            />
                          ) : (
                            item
                          )}
                        </div>
                      ))}
                    </div>
                  ) : typeof value === "object" && value !== null ? (
                    <div style={{ paddingLeft: `calc(1rem * ${indent})` }}>
                      <Title
                        order={3}
                        mb={"4"}
                        style={{
                          backgroundColor: "#fefefe",
                          border: "1px solid #efefef",
                          borderRadius: "5px",
                          padding: "5px 15px",
                          color: "#333",
                        }}
                      >
                        <i
                          className="fa-regular fa-file-lines me-2"
                          style={{ color: "#ecdd78" }}
                        ></i>{" "}
                        {key}
                      </Title>
                      {/* <Badge
                        className="fs-6"
                        color="yellow.6"
                        variant="dot"
                        size="xl"
                        mb={4}
                        fw={400}
                      >
                        {key}
                      </Badge> */}
                      <RenderObject
                        obj={value}
                        state={state}
                        indent={indent + 1}
                        editMode={tempEditMode}
                      />
                    </div>
                  ) : (
                    <Flex justify={"flex-start"} align={"center"}>
                      <div
                        style={{
                          backgroundColor: "#f9f9f9",
                          border: "1px solid #efefef",
                          borderRadius: "5px",
                          padding: "2px 5px 2px 15px",
                          marginRight: "10px",
                        }}
                      >
                        <Text
                          className="fs-5"
                          miw={"150px"}
                          // size="sm"
                          // className={treeNodeClass.idshort}
                        >
                          {key}
                        </Text>
                      </div>

                      {tempEditMode ? (
                        <input
                          className="fs-5 form-control"
                          id={stateKey}
                          value={innerState[stateKey] ?? value ?? ""}
                          onChange={(e) => {
                            setInnerState((prev) => ({
                              ...prev,
                              [e.target.id]: e.target.value,
                            }));
                            state[e.target.id] = e.target.value;
                          }}
                          onKeyDown={(e) => {
                            e.stopPropagation();
                          }}
                        />
                      ) : (
                        <Text
                          fw={600}
                          className="fs-5"
                          style={{ paddingLeft: "5px" }}
                        >
                          {innerState[stateKey] ?? value ?? ""}
                        </Text>
                      )}
                    </Flex>
                  )}
                </div>
              </Group>
            );
          })}
      </div>
    );
  }
);

// RenderNodeDetails: 노드의 상세 정보를 카드로 표시 (내부에서 RenderObject에 editMode 전달)
const RenderNodeDetails = memo(
  ({
    level,
    node,
    state,
    editMode,
  }: {
    level: number;
    node: any;
    state: any;
    editMode: boolean;
  }) => (
    <Card
      key={node.value}
      ml={`calc(3rem * ${level - 1})`}
      mb="xs"
      radius="md"
      padding="md"
      //shadow="sm"
      withBorder
      style={{
        borderColor: "#e6e6e6",
        borderWidth: "1px",
        backgroundColor: "#f1f1f1",
      }}
    >
      <Title
        order={3}
        mb={"sm"}
        style={{
          backgroundColor: "#fefefe",
          border: "1px solid #efefef",
          borderRadius: "5px",
          padding: "5px 15px",
          color: "#005f9f",
        }}
      >
        <i className="fa-regular fa-rectangle-list me-2"></i> {node.modelType}
      </Title>
      <RenderObject obj={node} state={state} editMode={editMode} />
    </Card>
  )
);

// RenderTreeNode: 개별 트리 노드를 렌더링, editMode 전달
const RenderTreeNode = memo(
  ({
    level,
    node,
    expanded,
    elementProps,
    state,
    editMode,
  }: {
    level: number;
    node: any;
    expanded: boolean;
    elementProps: any;
    state: any;
    editMode: boolean;
  }) => (
    <Box mb={"md"}>
      <Group
        mh="100px"
        h={"lg"}
        mb="md"
        pl={level === 2 ? "0.3rem" : `calc(4rem * ${level - 2})`}
        {...elementProps}
        onClick={(e) => {
          elementProps.onClick(e);
        }}
      >
        <div>
          <Flex h="100%" align="center">
            {level > 1 && <IconCurrencyLeu color="gray" />}
            {expanded ? <IconSquareRoundedMinus /> : <IconSquareRoundedPlus />}
            <Box h="100%" className={treeNodeClass.item}>
              <Badge
                className={treeNodeClass.modelType}
                variant="light"
                radius="sm"
                size="lg"
                ml={"xs"}
              >
                {node.modelType}
              </Badge>
              <Text className={"fs-5"} fw={700}>
                {node.idShort}
              </Text>
              <Text
                className={"fs-8"}
                c={"gray.7"}
                style={{ textAlign: "left" }}
              >
                {node.id}
              </Text>
            </Box>
          </Flex>
        </div>
      </Group>
      {expanded &&
        ["AssetAdministrationShell", "Submodel", "ConceptDescription"].map(
          (type) =>
            type in node ? (
              <RenderNodeDetails
                key={type}
                level={level}
                node={node[type]}
                state={state}
                editMode={editMode}
              />
            ) : (
              ""
            )
        )}
    </Box>
  )
);

// AASTree: Tree 컴포넌트를 감싸고, renderNode에 editMode 전달
interface AASTreeProps {
  data: any;
  treeDataRefCurrent: any;
  editMode: boolean;
  [key: string]: any;
}

function AASTree({
  data,
  treeDataRefCurrent,
  editMode,
  ...styleProps
}: AASTreeProps) {
  const tree = useTree({});

  useEffect(() => {
    tree.expand(data[0].value);

    // if (treeDataRefCurrent) {
    //   treeDataRefCurrent = {};
    // }
  }, [data, treeDataRefCurrent]);

  return (
    <Box {...styleProps}>
      <Tree
        mt="xs"
        data={data}
        tree={tree}
        renderNode={(props) => (
          <RenderTreeNode
            {...props}
            state={treeDataRefCurrent ?? {}}
            editMode={editMode}
          />
        )}
      />
    </Box>
  );
}

export default memo(AASTree);
