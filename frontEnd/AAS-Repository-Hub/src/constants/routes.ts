// src/constants/routes.ts

import { UserRole } from "./roles";

export const ROUTES = {
  UNAUTHORIZED: "/unauthorized",
  HOME: "/",
  ABOUT: "/about",
  SAMPLE: "/sample",
  LOGIN: "/login",
  LOGOUT: "/logout",
  SIGNUP: "/signup",
  RESET_PASSWORD: "/reset-password",
  TEST: {
    LOGIN: "/test/login",
  },

  AASMODEL: {
    LIST: "/aas",
    CREATE: "/aas/ins",
    VIEW: (modelSeq: string) => `/aas/${modelSeq}`,
    EDIT: (modelSeq: string) => `/aas/${modelSeq}/edit`,
  },

  SUBMODEL: {
    LIST: "/submodel",
    CREATE: "/submodel/ins",
    VIEW: (modelSeq: string) => `/submodel/${modelSeq}`,
    EDIT: (modelSeq: string) => `/submodel/${modelSeq}/edit`,
  },

  INSTANCE: {
    LIST: "/instance",
    CREATE: "/instance/ins",
    SERVER: "/instance/server",
    VIEW: (id: string) => `/instance/${id}`,
    EDIT: (instanceSeq: string) => `/instance/${instanceSeq}/edit`,
  },

  DISTRIBUTE: {
    LIST: "/distribute",
    CREATE: "/distribute/ins",
    VIEW: ({
      modelType,
      targetSeq,
    }: {
      modelType: "aasmodel" | "submodel";
      targetSeq: string;
    }) => `/distribute/${modelType}/${targetSeq}`,
    EDIT: ({
      modelType,
      targetSeq,
    }: {
      modelType: "aasmodel" | "submodel";
      targetSeq: string;
    }) => `/distribute/${modelType}/${targetSeq}/edit`,
  },

  USER: {
    LIST: "/user",
    CREATE: "/user/ins",
    VIEW: (id: string) => `/user/${id}`,
    EDIT: (id: string) => `/user/${id}/edit`,
  },
};

export const PROTECTED_ROUTES = [
  { path: ROUTES.HOME, minRole: undefined, allowRoles: [] },
  { path: ROUTES.ABOUT, minRole: undefined, allowRoles: [] },
  { path: ROUTES.SAMPLE, minRole: undefined, allowRoles: [] },
  { path: ROUTES.LOGIN, minRole: undefined, allowRoles: [] },
  { path: ROUTES.LOGOUT, minRole: undefined, allowRoles: [] },
  { path: ROUTES.SIGNUP, minRole: undefined, allowRoles: [] },

  { path: ROUTES.AASMODEL.LIST, minRole: undefined, allowRoles: [] },
  {
    path: ROUTES.AASMODEL.CREATE,
    minRole: UserRole.Approvedor,
    allowRoles: [],
  },
  {
    path: ROUTES.AASMODEL.VIEW(":modelSeq"),
    minRole: UserRole.User,
    allowRoles: [],
  },
  {
    path: ROUTES.AASMODEL.EDIT(":modelSeq"),
    minRole: UserRole.Approvedor,
    allowRoles: [],
  },

  { path: ROUTES.SUBMODEL.LIST, minRole: undefined, allowRoles: [] },
  {
    path: ROUTES.SUBMODEL.CREATE,
    minRole: UserRole.Approvedor,
    allowRoles: [],
  },
  {
    path: ROUTES.SUBMODEL.VIEW(":modelSeq"),
    minRole: UserRole.User,
    allowRoles: [],
  },
  {
    path: ROUTES.SUBMODEL.EDIT(":modelSeq"),
    minRole: UserRole.Approvedor,
    allowRoles: [],
  },

  { path: ROUTES.INSTANCE.LIST, minRole: UserRole.User, allowRoles: [] },
  { path: ROUTES.INSTANCE.CREATE, minRole: UserRole.User, allowRoles: [] },
  { path: ROUTES.INSTANCE.SERVER, minRole: UserRole.User, allowRoles: [] },
  { path: ROUTES.INSTANCE.VIEW(":id"), minRole: UserRole.User, allowRoles: [] },
  {
    path: ROUTES.INSTANCE.EDIT(":instanceSeq"),
    minRole: UserRole.User,
    allowRoles: [],
  },

  {
    path: ROUTES.DISTRIBUTE.LIST,
    minRole: UserRole.Approvedor,
    allowRoles: [],
  },
  {
    path: ROUTES.DISTRIBUTE.CREATE,
    minRole: UserRole.Approvedor,
    allowRoles: [],
  },
  {
    path: ROUTES.DISTRIBUTE.VIEW({
      modelType: "aasmodel",
      targetSeq: ":targetSeq",
    }),
    minRole: UserRole.Approvedor,
    allowRoles: [],
  },
  {
    path: ROUTES.DISTRIBUTE.EDIT({
      modelType: "aasmodel",
      targetSeq: ":targetSeq",
    }),
    minRole: UserRole.Approvedor,
    allowRoles: [],
  },

  { path: ROUTES.USER.LIST, minRole: UserRole.Approvedor, allowRoles: [] },
  { path: ROUTES.USER.CREATE, minRole: UserRole.Approvedor, allowRoles: [] },
  { path: ROUTES.USER.VIEW(":id"), minRole: UserRole.User, allowRoles: [] },
  {
    path: ROUTES.USER.EDIT(":id"),
    minRole: UserRole.Approvedor,
    allowRoles: [],
  },
];

export const routeAuthRegex = (pattern: string): RegExp => {
  // 특수 문자 이스케이프 (단, ":"는 이스케이프하지 않음)
  const escaped = pattern.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  // ":param"을 "[^/]+"로 변환하여 URL 세그먼트와 매칭되도록 처리
  const withParams = escaped.replace(/:([a-zA-Z0-9_]+)/g, "[^/]+");

  return new RegExp(`^${withParams}$`);
};

export type AccessResult = "allow" | "forbidden";

export const canAccessPath = (
  path: string,
  userRole: UserRole | undefined
): AccessResult => {
  const matchedRoute = PROTECTED_ROUTES.find((route) => {
    const regex = routeAuthRegex(route.path);
    return regex.test(path);
  });

  if (!matchedRoute) {
    return "allow"; // 디폴트로 허용
  }

  const { minRole, allowRoles = [] } = matchedRoute;

  if (minRole == undefined && allowRoles.length == 0) return "allow";
  if (allowRoles.includes(userRole)) return "allow";
  if (minRole !== undefined && userRole !== undefined && userRole <= minRole)
    return "allow";

  return "forbidden";
};
