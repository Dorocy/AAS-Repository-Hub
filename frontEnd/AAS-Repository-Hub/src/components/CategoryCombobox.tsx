import { getCodeList } from "@/api";
import { getCodeTree } from "@/utils";
import {
  useCombobox,
  Combobox,
  Tree,
  Group,
  Flex,
  Box,
  useTree,
  Text,
  Input,
  CheckIcon,
} from "@mantine/core";
import { IconChevronDown, IconLeaf } from "@tabler/icons-react";
import { useQuery } from "@tanstack/react-query";
import React, { ReactNode, useEffect, useMemo, useState } from "react";
import mantineTreeClasses from "@/css/MantineTree.module.css";

function CategoryCombobox({
  className = "",
  disabled = false,
  selectLeafOnly = false,
  value,
  setValue,
}: {
  className?: string;
  disabled?: boolean;
  selectLeafOnly?: boolean;
  value: any;
  setValue: Function;
}) {
  const combobox = useCombobox({});
  const codeTree = useTree();

  const [label, setLabel] = useState("");
  const [search, setSearch] = useState("");
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  const { data: categorys2 } = useQuery({
    queryKey: ["common/code", "category2"],
    queryFn: () => getCodeList("category2"),
  });

  const categoryTree = useMemo(
    () =>
      getCodeTree(
        Array.isArray(categorys2)
          ? categorys2.filter((item) =>
              item.title.toLowerCase().includes(search.toLowerCase())
            )
          : categorys2
      ),
    [categorys2, search, value]
  );

  useEffect(() => {
    if (categorys2) {
      setLabel(categorys2.find((item) => item.value === value)?.title);
    }
  }, [value, categorys2]);

  return (
    <Combobox
      zIndex={2000}
      width={500}
      store={combobox}
      resetSelectionOnOptionHover
      onOptionSubmit={(val) => {
        setValue(val);
        setLabel(categorys2.find((item) => item.c_id === val)?.title);
        setSearch("");
        combobox.updateSelectedOptionIndex("active");
        combobox.closeDropdown();
      }}
    >
      <Combobox.Target>
        <Flex
          align="center"
          w={"100%"}
          bd={className == "border-0" ? "" : "1px solid gray.4"}
          style={{
            borderRadius: "8px",
          }}
        >
          <input
            className={"form-control border-0 flex-grow-1"}
            disabled={disabled}
            placeholder="Category All"
            value={label || search}
            onChange={(e) => {
              setLabel("");
              setSearch(e.currentTarget.value);
              codeTree.expandAllNodes();
            }}
            onKeyDown={() => {
              codeTree.expandAllNodes();
            }}
            onClick={() => {
              codeTree.expandAllNodes();

              combobox.openDropdown();
            }}
            onFocus={() => {
              codeTree.expandAllNodes();

              combobox.openDropdown();
            }}
            onBlur={() => {
              setLabel(categorys2.find((item) => item.value === value)?.title);
              setSearch(search);
              codeTree.expandAllNodes();

              combobox.closeDropdown();
            }}
          />
          {value !== "" && (
            <Input.ClearButton
              style={{ cursor: "pointer" }}
              size="1.5rem"
              onClick={() => {
                setSearch("");
                setValue(undefined);
              }}
            />
          )}
          <Combobox.Chevron
            size="2.5rem"
            style={{ cursor: "pointer" }}
            onClick={() => combobox.openDropdown()}
          />
        </Flex>
      </Combobox.Target>

      <Combobox.Dropdown>
        <Combobox.Options mah={500} style={{ overflowY: "auto" }}>
          {/* 공통코드 트리 */}
          {Array.isArray(categoryTree) && (
            <Tree
              data={categoryTree || []}
              tree={codeTree}
              expandOnClick={false}
              renderNode={({
                level,
                node,
                hasChildren,
                expanded,
                elementProps,
                tree,
              }) => {
                const optionContent = (
                  <Flex align={"center"}>
                    {!isNaN(Number(node.value)) && (
                      <IconLeaf size={"1rem"} color="green" />
                    )}
                    <Text ml={6}>{node.label}</Text>
                    {node.value === value && (
                      <CheckIcon size="1rem" style={{ marginLeft: "0.5rem" }} />
                    )}
                  </Flex>
                );
                const wrapped =
                  selectLeafOnly && isNaN(Number(node.value)) ? (
                    <div key={node.value}>{optionContent}</div>
                  ) : (
                    <Combobox.Option
                      value={node.value}
                      key={node.value}
                      active={node.value === value}
                    >
                      {optionContent}
                    </Combobox.Option>
                  );
                const childNode = (
                  <Group>
                    <Flex h="100%" align="center">
                      {hasChildren && (
                        <IconChevronDown
                          size={14}
                          style={{
                            marginRight: 4,
                            transform: expanded
                              ? "rotate(0deg)"
                              : "rotate(-90deg)",
                          }}
                          onClick={() => {
                            tree.toggleExpanded(node.value);
                          }}
                        />
                      )}{" "}
                      {wrapped}
                    </Flex>
                  </Group>
                );
                return (
                  <div key={node.value}>
                    {Array.from({
                      length: level - 1,
                    }).reduce<ReactNode>((child, _, index) => {
                      return (
                        <Box
                          className={
                            level - index + 1 > 1
                              ? mantineTreeClasses.treeLine
                              : ""
                          }
                          pl={20}
                        >
                          {child}
                        </Box>
                      );
                    }, childNode)}
                  </div>
                );
              }}
            />
          )}
        </Combobox.Options>
      </Combobox.Dropdown>
    </Combobox>
  );
}
export default CategoryCombobox;
