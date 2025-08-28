import React from "react";

export type MessageSender = "user" | "assistant";
export type TextFormat = "Text" | "Table" | "Json";

export interface Message {
    id: string;
    role: MessageSender;
    timestamp: number;
    content: string;
    format: TextFormat;
}

type ExampleItem = {
    icon: React.ReactNode;
    title: string;
    subtitle?: string;
    prompt: string;
};
