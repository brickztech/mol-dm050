import React from "react";
import { toast } from "react-toastify";

type ErrorBoundaryProps = {
  children: React.ReactNode;
};

export default class ErrorBoundary extends React.Component<ErrorBoundaryProps> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: any, errorInfo: any) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);

    toast.error(`Markdown error: ${error.message}`, {
      position: "bottom-right",
      autoClose: 5000,
      toastId: "markdown-error",
    });
  }

  render() {
    return this.props.children;
  }
}
