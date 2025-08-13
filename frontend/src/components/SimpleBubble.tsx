import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { Box, IconButton, Sheet, Tooltip } from "@mui/joy";
import copy from "copy-to-clipboard";
import { motion } from "framer-motion";
import { toast } from "react-toastify";
import type { MessageSender } from "src/pages/chat";
import ErrorBoundary from "./ErrorComponent";

interface SimpleBubbleProps {
  sender: MessageSender;
  message: any;
}

export default function SimpleChatBubble({
  sender,
  message,
}: SimpleBubbleProps) {
  const isUser = String(sender).toLowerCase() === "user";

  const handleCopy = () => {
    if (!message) {
      toast.error("Nothing to copy!", { theme: "light" });
      return;
    }
    if (copy(message)) {
      toast.success("Copied to clipboard!", {
        autoClose: 2000,
        theme: "light",
      });
    } else {
      toast.error("Failed to copy!", { theme: "light" });
    }
  };

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
        <Box
          className={`${isUser ? "user-bubble" : "assistant-bubble"}`}
          sx={{
            position: "relative",
            width: "100%",
            maxWidth: { xs: "98%", sm: "92%", md: 900, lg: 1000 },
            borderRadius: 3,
            boxShadow: "0 2px 16px 0 rgba(30,30,50,0.10)",
            px: { xs: 2, sm: 3 },
            py: 2.5,
            "&:hover .copy-btn": { opacity: 1 },
            minHeight: 45,
          }}
        >
          <Box
            className="copy-btn"
            sx={{
              position: "absolute",
              top: 10,
              right: 15,
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
            <Box
              sx={{
                wordBreak: "break-word",
                whiteSpace: "pre-line",
                width: "100%",
              }}
              dangerouslySetInnerHTML={{ __html: String(message) }}
            />
          </ErrorBoundary>
        </Box>
      </Box>
    </motion.div>
  );
}
