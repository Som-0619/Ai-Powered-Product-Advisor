"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  Sparkles,
  Loader2,
  AlertCircle,
  HelpCircle,
  Search,
  MessageSquare,
  ShieldCheck,
  FileCheck2,
  Sliders,
  CheckCircle2,
} from "lucide-react";
import { RecommendationCard } from "./RecommendationCard";
import {
  streamRecommendation,
  RecommendationItem,
  RecommendationResponse,
  TraceStep,
} from "../services/api";

interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  recommendations?: RecommendationItem[];
  clarificationQuestion?: string;
  status?: "streaming" | "completed" | "error";
  currentStepMessage?: string;
  trace?: TraceStep[];
  timestamp: string;
}

interface ChatInterfaceProps {
  onOpenDetails: (item: RecommendationItem) => void;
  onOpenEvidence: (item: RecommendationItem) => void;
  onOpenReviews: (item: RecommendationItem) => void;
  onOpenCompatibility: (item: RecommendationItem) => void;
  onOpenVision: (item: RecommendationItem) => void;
  onUpdateGlobalTrace?: (trace: TraceStep[]) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onOpenDetails,
  onOpenEvidence,
  onOpenReviews,
  onOpenCompatibility,
  onOpenVision,
  onUpdateGlobalTrace,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "initial-welcome",
      sender: "assistant",
      text: "Hello! I am your AI Product Advisor. I provide grounded recommendations for consumer electronics and electronic components with real-time verification and live price comparison across Amazon and Flipkart. What can I help you find?",
      // Left blank on initial render (server and client can disagree on locale/24h
      // formatting) and filled in on mount below, to avoid a hydration mismatch.
      timestamp: "",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [liveStepMessage, setLiveStepMessage] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === "initial-welcome" && !msg.timestamp
          ? { ...msg, timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }
          : msg
      )
    );
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, liveStepMessage]);

  const handleSend = async (userText?: string) => {
    const textToSend = (userText || input).trim();
    if (!textToSend || isLoading) return;

    setInput("");
    const userMsgId = `user-${Date.now()}`;
    const assistantMsgId = `asst-${Date.now()}`;

    // Append user message
    const userMsg: ChatMessage = {
      id: userMsgId,
      sender: "user",
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    // Append placeholder assistant message
    const placeholderAssistantMsg: ChatMessage = {
      id: assistantMsgId,
      sender: "assistant",
      text: "",
      status: "streaming",
      currentStepMessage: "Finding recommendations...",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg, placeholderAssistantMsg]);
    setIsLoading(true);

    await streamRecommendation(textToSend, {
      onStep: () => {
        setLiveStepMessage("Finding recommendations...");
      },
      onComplete: (result: RecommendationResponse) => {
        setIsLoading(false);
        setLiveStepMessage("");

        let responseText = "";
        if (result.status === "clarification") {
          responseText =
            result.clarification_question ||
            "Could you provide a bit more detail on your budget, category, or preferred features?";
        } else if (result.status === "no_results") {
          responseText =
            result.message ||
            "I searched our catalog but could not find items matching your strict constraints. Would you like to adjust your budget or requirements?";
        } else {
          const count = result.recommendations?.length || 0;
          responseText = `I completed the multi-agent verification pipeline. Here are the top evaluated recommendations with live price comparisons for Amazon and Flipkart:`;
        }

        setMessages((prev) =>
          prev.map((msgItem) =>
            msgItem.id === assistantMsgId
              ? {
                  ...msgItem,
                  status: "completed",
                  text: responseText,
                  recommendations: result.recommendations,
                  clarificationQuestion: result.clarification_question,
                  trace: result.trace,
                  currentStepMessage: undefined,
                }
              : msgItem
          )
        );

        if (onUpdateGlobalTrace && result.trace) {
          onUpdateGlobalTrace(result.trace);
        }
      },
      onError: (err) => {
        setIsLoading(false);
        setLiveStepMessage("");
        setMessages((prev) =>
          prev.map((msgItem) =>
            msgItem.id === assistantMsgId
              ? {
                  ...msgItem,
                  status: "error",
                  text: `An error occurred while evaluating your request: ${err.message}. Please verify the backend service is running.`,
                  currentStepMessage: undefined,
                }
              : msgItem
          )
        );
      },
    });
  };

  return (
    <div className="flex flex-col h-[750px] bg-surface-50 border border-slate-200/80 dark:border-white/10 rounded-2xl overflow-hidden shadow-sm transition-colors duration-200">
      {/* Chat Messages List */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start space-x-3 ${
              msg.sender === "user" ? "flex-row-reverse space-x-reverse" : ""
            }`}
          >
            {/* Avatar */}
            <div
              className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
                msg.sender === "user"
                  ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                  : "bg-surface-100 border border-slate-200/80 dark:border-white/10 text-indigo-600 dark:text-indigo-400"
              }`}
            >
              {msg.sender === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            {/* Message Bubble Container */}
            <div className={`max-w-2xl space-y-3 ${msg.sender === "user" ? "items-end" : "items-start"}`}>
              <div
                className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                  msg.sender === "user"
                    ? "bg-blue-600 text-white rounded-tr-none shadow-sm"
                    : "bg-surface-100 text-slate-800 dark:text-slate-200 border border-slate-200/60 dark:border-white/5 rounded-tl-none"
                }`}
              >
                {/* Live Real Progress Indicator */}
                {msg.status === "streaming" && (
                  <div className="flex items-center space-x-2 text-blue-600 dark:text-blue-400 py-1">
                    <Loader2 className="w-4 h-4 animate-spin shrink-0" />
                    <span className="font-semibold text-xs tracking-tight animate-pulse">
                      {msg.currentStepMessage || "Processing query..."}
                    </span>
                  </div>
                )}

                {msg.text && <p>{msg.text}</p>}

                {/* Clarification prompt card */}
                {msg.clarificationQuestion && (
                  <div className="mt-3 p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-start space-x-2.5">
                    <HelpCircle className="w-4 h-4 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="text-[11px] uppercase font-bold text-blue-600 dark:text-blue-300 block">
                        Clarification Needed
                      </span>
                      <p className="text-xs text-slate-900 dark:text-white mt-0.5">{msg.clarificationQuestion}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Recommendation Cards inside chat stream */}
              {msg.recommendations && msg.recommendations.length > 0 && (
                <div className="space-y-4 pt-1 w-full">
                  <div className="flex items-center space-x-2 text-xs text-slate-500 dark:text-slate-400 px-1">
                    <Sparkles className="w-3.5 h-3.5 text-blue-500" />
                    <span>Top Verified Matches ({msg.recommendations.length})</span>
                  </div>
                  <div className="grid grid-cols-1 gap-4">
                    {msg.recommendations.map((rec) => (
                      <RecommendationCard
                        key={rec.product_id}
                        item={rec}
                        onOpenDetails={onOpenDetails}
                        onOpenEvidence={onOpenEvidence}
                        onOpenReviews={onOpenReviews}
                        onOpenCompatibility={onOpenCompatibility}
                        onOpenVision={onOpenVision}
                      />
                    ))}
                  </div>
                </div>
              )}

              <span className="text-[10px] text-slate-400 dark:text-slate-500 px-1 block">
                {msg.timestamp}
              </span>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input Bar */}
      <div className="border-t border-slate-200/80 dark:border-white/5 p-3 sm:p-4 bg-surface-100/60 backdrop-blur-md">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center space-x-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            placeholder={
              isLoading
                ? "Finding recommendations..."
                : "Ask about a laptop, headphones, or electronic component (English or Hinglish)..."
            }
            className="flex-1 bg-surface-50 border border-slate-200/80 dark:border-white/10 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-blue-500/50 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-all disabled:opacity-40 disabled:hover:bg-blue-600 shrink-0 shadow-sm"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <span>Send</span>
                <Send className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
