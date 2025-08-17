import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { DataGrid } from "@mui/x-data-grid";
import copy from "copy-to-clipboard";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";
import { toast } from "react-toastify";
import remarkGfm from "remark-gfm";
import ErrorBoundary from "./ErrorComponent";
import type { MessageSender } from "src/pages/chat";
import { Box, IconButton, Sheet, Tooltip, Typography } from "@mui/joy";

interface ChatBubbleProps {
  sender: MessageSender;
  message: any;
  hitList?: any[];
}
function isHtml(text: string): boolean {
  return typeof text === "string" && /<\/?[a-z][\s\S]*>/i.test(text);
}

export default function ChatBubble({
  sender,
  message,
  hitList,
}: ChatBubbleProps) {
  const isUser = String(sender).toLowerCase() === "user";

  const handleCopy = () => {
    if (!markdown) {
      toast.error("Nothing to copy!", { theme: "light" });
      return;
    }
    if (copy(markdown)) {
      toast.success("Copied to clipboard!", {
        autoClose: 2000,
        theme: "light",
      });
    } else {
      toast.error("Failed to copy!", { theme: "light" });
    }
  };

  function extractMarkdown(message: any): string {
    if (typeof message === "string") return message;
    if (Array.isArray(message)) return message.join("\n");
    if (typeof message === "object" && message !== null) {
      if (typeof message.content === "string") return message.content;
      if (typeof message.query === "string") return message.query;
      for (const key of Object.keys(message)) {
        if (typeof message[key] === "string") return message[key];
      }
      for (const key of Object.keys(message)) {
        if (
          typeof message[key] === "object" &&
          message[key] &&
          typeof message[key].content === "string"
        ) {
          return message[key].content;
        }
      }
    }
    return "";
  }

  function parseMarkdownTable(markdown: any) {
    const lines: string[] = markdown.trim().split("\n");
    const separatorLineIndex = lines.findIndex((line) =>
      /^(\|\s*:?-+:?\s*)+\|?$/.test(line)
    );
    if (separatorLineIndex === -1) return null;

    const header = lines[separatorLineIndex - 1]
      .split("|")
      .map((cell) => cell.trim())
      .filter(Boolean);
    const rows = lines
      .slice(separatorLineIndex + 1)
      .filter((line) => line.trim().startsWith("|"))
      .map((line) =>
        line
          .split("|")
          .map((cell) => cell.trim())
          .filter(Boolean)
      );

    const columns = header.map((field) => ({
      field: field.toLowerCase().replace(/\s+/g, "_"),
      headerName: field,
      flex: 1,
      minWidth: 120,
    }));

    const dataRows = rows.map((row, idx) => {
      const rowObj: any = { id: idx };
      header.forEach((field, i) => {
        rowObj[field.toLowerCase().replace(/\s+/g, "_")] = row[i] || "";
      });
      return rowObj;
    });

    return { columns, rows: dataRows };
  }

  let markdown: string;
  try {
    markdown = extractMarkdown(message);
  } catch (e) {
    markdown = "[Error extracting message content]";
  }

  const isMarkdown =
    (markdown.includes("```") ||
      markdown.includes("#") ||
      markdown.includes("- ") ||
      markdown.includes("* ")) &&
    isHtml(markdown) === false;
  const parsedTable = !isUser && parseMarkdownTable(markdown);
  return (
    <motion.div
      style={{ maxWidth: "85%" }}
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <Box
        sx={{
          display: "flex",
          justifyContent: isUser ? "flex-end" : "flex-start",
          my: 2,
        }}
      >
        <Sheet
          sx={{
            position: "relative",
            width: "100%",
            maxWidth: { xs: "98%", sm: "92%", md: 900, lg: 1000 },
            bgcolor: isUser
              ? "rgba(59, 137, 154, 0.5)"
              : "rgba(0, 40, 71, 0.5)",
            color: "#ececec",
            borderRadius: 3,

            boxShadow: "0 2px 16px 0 rgba(30,30,50,0.10)",
            fontSize: "1.11rem",
            lineHeight: 1.65,
            px: { xs: 2, sm: 3 },
            py: 2.5,
            "&:hover .copy-btn": { opacity: 1 },
            minHeight: 45,
          }}
        >
          <Box
            className="copy-btn"
            sx={{
              position: "relative",
              top: 10,
              right: 15,
              padding: 0.5,
              margin:3,
              opacity: 0,
              transition: "opacity 0.18s",
              display: "flex",
              alignItems: "center",
            }}
          >
            <Tooltip title="Copy to clipboard" arrow>
              <IconButton onClick={handleCopy} sx={{ color: "#fff" }}>
                <ContentCopyIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
          <ErrorBoundary>
            {parsedTable ? (
              <Box sx={{ height: "auto", width: "100%", my: 1 }}>
                <DataGrid
                  rows={parsedTable.rows}
                  columns={parsedTable.columns}
                  initialState={{
                    pagination: {
                      paginationModel: { pageSize: 5 },
                    },
                  }}
                  pageSizeOptions={[5, 10, 20]}
                  disableRowSelectionOnClick
                  sx={{
                    backgroundColor: "rgba(36,53,74,0.97)",
                    borderRadius: 2,
                    "& .MuiDataGrid-cell": {
                      backgroundColor: "rgba(27,120,141,0.18)",
                      color: "#eee",
                      fontWeight: 400,
                    },
                    "& .MuiDataGrid-columnHeader": {
                      backgroundColor: "rgba(36,53,74,0.94)",
                      fontWeight: 600,
                    },
                    "& .MuiDataGrid-row:nth-of-type(odd)": {
                      backgroundColor: "rgba(240,248,255,0.07)",
                    },
                  }}
                />
              </Box>
            ) : isMarkdown ? (
              <ReactMarkdown
                children={markdown}
                remarkPlugins={[remarkGfm]}
                components={{
                  code: ({
                    node,
                    inline,
                    className,
                    children,
                    ...props
                  }: any) => {
                    const match = /language-(\w+)/.exec(className || "");
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={oneLight}
                        language={match[1]}
                        PreTag="div"
                        customStyle={{
                          borderRadius: 8,
                        }}
                      >
                        {String(children).replace(/\n$/, "")}
                      </SyntaxHighlighter>
                    ) : (
                      <code
                        className={className}
                        {...props}
                        style={{
                          background: "rgba(27,120,141,0.56)",
                          color: "#baffc9",
                          borderRadius: 5,
                          padding: "0.11em 0.4em",
                          fontSize: "1em",
                        }}
                      >
                        {children}
                      </code>
                    );
                  },
                }}
              />
            ) : (
              <div
                dangerouslySetInnerHTML={{ __html: markdown }}
                style={{ wordBreak: "break-word" }}
              />
              
            )}
          </ErrorBoundary>
        </Sheet>
      </Box>
    </motion.div>
  );
}
