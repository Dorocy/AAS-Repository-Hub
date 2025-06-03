// import { readFile } from 'fs/promises'

// const filePath = new URL('./data.json', import.meta.url)
// const rawData = await readFile(filePath, 'utf-8')
// const json = JSON.parse(rawData)

export const addValuePaths = (obj, basePath = "") => {
  if (Array.isArray(obj)) {
    return obj.map((item, index) =>
      addValuePaths(item, `${basePath}[${index}]`)
    );
  } else if (typeof obj === "object" && obj !== null) {
    let newObj = {};
    for (let key in obj) {
      let newBasePath = basePath != "" ? `${basePath}.${key}` : key;
      newObj[key] = addValuePaths(obj[key], newBasePath);
    }
    newObj.valuePath = basePath;

    return newObj;
  }

  return obj;
};

export const parsingSub = (obj) => {
  if (!obj) return null; // ✅ null 체크 추가

  const { modelType, idShort } = obj;
  let id = "";
  if ("id" in obj) {
    id = obj.id;
  } else if (obj.semanticId?.keys?.length > 0) {
    id = obj.semanticId.keys[0].value;
  }

  const label = `[${modelType}] ${idShort} ${id}`;

  const treeNode = {
    label,
    value: obj.valuePath,
    valuePath: obj.valuePath,
    id,
    idShort,
    modelType,
  };

  let tempNode = { ...obj };

  let arr;
  switch (obj.modelType) {
    case "Submodel":
      arr = obj.submodelElements;
      delete tempNode.submodelElements;
      break;
    case "SubmodelElementCollection":
    case "SubmodelElementList":
      arr = obj.value;
      delete tempNode.value;
      break;
    case "Entity":
      arr = obj.statements;
      delete tempNode.statements;
      break;
    default:
      break;
  }

  treeNode["Submodel"] = tempNode;

  if (Array.isArray(arr)) {
    treeNode.children = arr.map(parsingSub).filter(Boolean); // ✅ 빈 값 제거
  }

  return treeNode;
};

export function parsingAAS(json) {
  const { assetAdministrationShells, submodels, conceptDescriptions } = json;

  const parsingSub = (obj) => {
    if (!obj) return null; // ✅ null 체크 추가

    const { modelType, idShort } = obj;
    let id = "";
    if ("id" in obj) {
      id = obj.id;
    } else if (obj.semanticId?.keys?.length > 0) {
      id = obj.semanticId.keys[0].value;
    }

    const label = `[${modelType}] ${idShort} ${id}`;

    const treeNode = {
      label,
      value: obj.valuePath,
      valuePath: obj.valuePath,
      id,
      idShort,
      modelType,
    };

    let tempNode = { ...obj };

    let arr;
    switch (obj.modelType) {
      case "Submodel":
        arr = obj.submodelElements;
        delete tempNode.submodelElements;
        break;
      case "SubmodelElementCollection":
      case "SubmodelElementList":
        arr = obj.value;
        delete tempNode.value;
        break;
      case "Entity":
        arr = obj.statements;
        delete tempNode.statements;
        break;
      default:
        break;
    }

    treeNode["Submodel"] = tempNode;

    if (obj.semanticId?.keys?.length > 0) {
      const { type, value } = obj.semanticId.keys[0];
      if (type === "ConceptDescription") {
        const find = conceptDescriptions.find((item) => item.id == value);
        if (find != null) {
          treeNode["ConceptDescription"] = find;
        }
      }
    }

    if (Array.isArray(arr)) {
      treeNode.children = arr.map(parsingSub).filter(Boolean); // ✅ 빈 값 제거
    }

    return treeNode;
  };

  const parsingSubmodel = (submodel, submodels) => {
    const { type, value } = submodel.keys[0];
    const foundSubmodel = submodels.find(
      (s) => s.modelType === type && s.id === value
    );

    if (!foundSubmodel) return [];

    return parsingSub(foundSubmodel);
  };

  const treeNodeList = assetAdministrationShells.map((aas) => {
    const { modelType, idShort, id } = aas;
    const label = `[${modelType}] ${idShort} ${id}`;
    const value = aas.valuePath;

    const treeNode = { label, value, modelType, idShort, id };
    let tempTreeNode = { ...aas };
    delete tempTreeNode["submodels"];
    treeNode["AssetAdministrationShell"] = tempTreeNode;
    const treeData = aas.submodels
      .map((submodel) => parsingSubmodel(submodel, submodels))
      .flat(); // ✅ 빈 배열 방지 + 중첩 배열 해제
    treeNode.children = treeData;
    return treeNode;
  });
  return treeNodeList;
}
