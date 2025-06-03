// src/utils/toast.ts

import toast, { ToastOptions, Toast } from "react-hot-toast";
import { Notification } from "@mantine/core";
import {
  IconCheck,
  IconExclamationMark,
  IconLoader,
  IconX,
} from "@tabler/icons-react";

const typeOption = {
  loading: {
    icon: <IconLoader size={20} />,
    color: "#424242",
  },

  success: {
    icon: <IconCheck size={20} />,
    color: "#099268",
  },
  warning: {
    icon: <IconExclamationMark size={20} />,
    color: "#e67700",
  },
  error: {
    icon: <IconX size={20} />,
    color: "#c92a2a",
  },
};

type MessageType = keyof typeof typeOption;

const createToast = (type: MessageType) => {
  return (message: string, options?: ToastOptions) => {
    const { icon, color } = typeOption[type];

    return toast.custom(
      (t: Toast) => (
        <Notification
          icon={icon}
          loading={type === "loading"}
          color={color}
          mt="md"
          p={16}
          style={{ border: `1px solid ${color}` }}
          onClose={() => toast.dismiss(t.id)}
        >
          <span className="fs-5" style={{ color }}>
            {message}
          </span>
        </Notification>
      ),
      options
    );
  };
};

// ✅ 타입만 명확히 제한된 객체
export const showToast: {
  loading: (msg: string, opt?: ToastOptions) => string;
  success: (msg: string, opt?: ToastOptions) => string;
  warning: (msg: string, opt?: ToastOptions) => string;
  error: (msg: string, opt?: ToastOptions) => string;
} = {
  loading: createToast("loading"),
  success: createToast("success"),
  warning: createToast("warning"),
  error: createToast("error"),
};
