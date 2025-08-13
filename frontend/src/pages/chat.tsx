import { Box, Button, LinearProgress, Textarea } from "@mui/joy";
import { AnimatePresence, motion } from "framer-motion";
import { useCallback, useRef, useState } from "react";
import { askQuestionStream } from "../api/api";
import ChatBubble from "../components/ChatBubble";
import MotionWrapper from "../components/MotionWrapper";
import { FullSizeCentered } from "../components/styled";
import "./style.css";
import SimpleChatBubble from "src/components/SimpleBubble";


export type MessageSender = "user" | "assistant";

export interface Message {
  role: MessageSender;
  timestamp?: number;
  content: string;
  format: TextFormat;
}

export interface BubbleProps {
  key: string;
  sender: MessageSender;
  message: string;
  hitList?: any[];
}
export type TextFormat = "Text" | "Table" | "Json";

export interface LLMResponse {
  answer: string | any[];
  format: TextFormat;
}

function renderBubble({ key, sender, message, hitList }: BubbleProps) {
  return (
    <Box
      key={key}
      sx={{
        display: "flex",
        justifyContent: sender === "user" ? "flex-end" : "flex-start",
        width: "100%",
      }}
    >
      <SimpleChatBubble sender={sender} message={message}/>
    </Box>
  );
}

export default function Text2SqlPageMol() {
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement | null>(null);
  const [history, setHistory] = useState<Message[]>([]);
  const [initialMessage, setInitialMessage] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const [lastChunks, setLastChunks] = useState<string | null>(null);
  const [input, setInput] = useState("");

  const addMessage = useCallback(
    (query: string, format: TextFormat, sender: MessageSender) => {
      const newMessage: Message = {
        role: sender,
        content: query,
        timestamp: Date.now(),
        format: format,
      };
      setHistory((prev) => [...prev, newMessage]);
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop =
          chatContainerRef.current.scrollHeight;
      }
    },
    [setHistory, chatContainerRef]
  );

  const handleStop = () => {
    setIsLoading(false);
    setInitialMessage(null);
    setInput("");
  };
  
  const handleSend = async () => {
    if (!input.trim()) return;

    setIsLoading(true);
    
    try {
      if (lastChunks && lastChunks !== '') {
        addMessage(lastChunks, "Text", "assistant");
        setLastChunks(null);
      }

      addMessage(input, "Text", "user");
      setInput("");
      const stream = await askQuestionStream(input, history);

      if (stream) {
        const decoder = new TextDecoder();
        let received = "";

        while (true) {
          const { done, value } = await stream.read();
          if (done) break;
          received += decoder.decode(value, { stream: true });
          
          setLastChunks(received);
        }
      }
      setIsLoading(false);
    } catch (err: any) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  return (
    <Box>
      <MotionWrapper>
        <FullSizeCentered>
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "flex-start",
              width: "100%",
              padding: "1rem",
              position: "relative",
            }}
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              style={{ width: "100vw" }}
            >
              <Box
                sx={{
                  position: "relative",
                  backdropFilter: "blur(10px)",
                  display: "flex",
                  flexDirection: "column",
                  gap: 2,
                }}
              >
                <Box
                  ref={chatContainerRef}
                  className={isLoading ? "loading-border" : ""}
                  sx={{
                    height: "60vh",
                    width: "100%",
                    maxWidth: "100%",
                    display: "flex",
                    flexDirection: "column",
                    gap: 1,
                    overflowY: "auto",
                    padding: 0.5,
                    border: "none",
                  }}
                >
                  <AnimatePresence initial={false}>
                    {initialMessage && (
                      <Box
                        key="initial-message"
                        sx={{
                          display: "flex",
                          justifyContent: "flex-start",
                          width: "100%",
                        }}
                      >
                        <SimpleChatBubble
                          sender={"assistant"}
                          message={initialMessage}
                        />
                      </Box>
                    )}
                    {history.map((msg, idx) => {
                      return renderBubble({
                        key: `msg-${idx}`,
                        sender: msg.role || "user",
                        message: msg.content,
                        hitList: [],
                      } as BubbleProps);
                    })}
                    {lastChunks && renderBubble({
                        key: `msg-last`,
                        sender: "assistant",
                        message: lastChunks,
                        hitList: [],
                      } as BubbleProps)}

                  </AnimatePresence>

                  <div ref={messagesEndRef} style={{ height: "200px" }} />
                </Box>
                <Box
                  sx={{
                    width: "100%",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    minHeight: 3,
                  }}
                >
                  <LinearProgress
                    variant={isLoading ? "soft" : "solid"}
                    value={isLoading ? undefined : 0}
                    sx={{
                      height: 2,
                      background: "rgba(255,255,255,0.07)",
                      opacity: isLoading ? 1 : 0.7,
                      transition: "opacity 0.2s",
                      width: "95%",
                      "& .MuiLinearProgress-bar1Indeterminate, & .MuiLinearProgress-bar2Indeterminate":
                        {
                          background:
                            "linear-gradient(90deg, #A47451FF 0%, #3B899AFF 100%)",
                        },
                      "& .MuiLinearProgress-bar": {
                        background:
                          "linear-gradient(90deg, #A47451FF 0%, #3B899AFF 100%)",
                      },
                    }}
                  />
                </Box>
                <Box
                  sx={{
                    flex: 1,
                    display: "flex",
                    flexDirection: "row",
                    justifyContent: "space-between",
                  }}
                >
                  <Textarea
                    value={input}
                    maxRows={3}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey && !isLoading) {
                        e.preventDefault();
                        handleSend();
                      }
                    }}
                    disabled={isLoading}
                    placeholder="Type your message..."
                    variant="outlined"
                    sx={{
                      flex: 1,
                      input: {
                        "&:-webkit-autofill": {
                          boxShadow: "0 0 0 100px rgba(255,255,255,0.1) inset",
                          WebkitTextFillColor: "#fff",
                          caretColor: "#fff",
                        },
                      },
                    }}
                  />

                  <Button
                    variant="outlined"
                    onClick={isLoading ? handleStop : handleSend}
                    sx={{
                      borderColor: isLoading
                        ? "#FF06068C"
                        : "rgba(255, 255, 255, 0.3)",
                      backgroundColor: "transparent",
                      color: isLoading ? "#FF06068C" : "",
                      backdropFilter: "blur(4px)",
                      padding: "8px 20px",
                      textTransform: "none",
                      fontWeight: 500,
                      marginLeft: "1em",
                      transition: "all 0.2s ease-in-out",
                      "&:hover": {
                        borderColor: "#90caf9",
                        backgroundColor: "rgba(144, 202, 249, 0.1)",
                      },
                    }}
                    disabled={input.trim().length === 0 || isLoading}
                  >
                    {isLoading ? "Stop" : "Send"}
                  </Button>
                </Box>
              </Box>
            </motion.div>
          </Box>
        </FullSizeCentered>
      </MotionWrapper>
    </Box>
  );
}
