import { ChatComposer, ChatLayout, ChatMessage, ChatMessageBubble, ChatMessageList, ChatMessageMetadata, ChatSystemMessage, ChatToolCalls } from "@astryxdesign/core/Chat";
import { Markdown } from "@astryxdesign/core/Markdown";
import React from "react";
import { chatMessages, modelProps } from "../astryx_bridge.mjs";

function AstryxChatView({ model }) {
  const props = modelProps(model);
  const isStreaming = Boolean(model.get("is_streaming"));
  const messages = chatMessages(model.get("messages"));
  const lastIndex = messages.length - 1;
  const rows = messages.map((message, index) => {
    if (message.role === "system") {
      return React.createElement(ChatSystemMessage, { key: message.key }, message.content);
    }
    const metadata = message.status || message.isStopped
      ? React.createElement(ChatMessageMetadata, {
        status: message.status,
        footer: message.isStopped ? "Stopped" : undefined,
      })
      : undefined;
    return React.createElement(
      ChatMessage,
      { key: message.key, sender: message.role },
      React.createElement(
        ChatMessageBubble,
        { metadata },
        React.createElement(Markdown, { isStreaming: isStreaming && index === lastIndex }, message.content),
      ),
      message.toolCalls.length > 0 ? React.createElement(ChatToolCalls, { calls: message.toolCalls }) : null,
    );
  });
  const composer = React.createElement(ChatComposer, {
    placeholder: String(model.get("placeholder") || "") || undefined,
    isDisabled: Boolean(model.get("disabled")),
    isStopShown: isStreaming,
    onSubmit: (value) => model.send({ type: "submit", value }),
    onStop: () => model.send({ type: "stop" }),
  });
  return React.createElement(
    ChatLayout,
    { ...props, composer, style: { height: "100%", ...props.style } },
    React.createElement(ChatMessageList, { isStreaming }, rows),
  );
}

export const SPECS = {
  Chat: { view: AstryxChatView },
};
