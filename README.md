# Gemini English Tutor Bot 🤖📝

A lightweight, production-ready Telegram Bot designed to act as your personal, patient English teacher. Powered by Google's **Gemini 1.5 Flash API**, this bot helps you improve your daily conversational English through smooth chatting and instant, actionable feedback.

## ✨ Core Features
- **Smart English Coach:** Engages in natural, 2-3 sentence casual conversations using daily colloquial English.
- **Correction Feedback Loop:** Detects grammatical errors or unnatural phrasing, gently points them out in **Chinese**, offers the most natural bolded expression, and keeps the conversation flowing in English.
- **Lag-Free Experience:** Implements a strict sliding-window memory mechanism (retains only the last N rounds), ensuring ultra-fast responses and preventing context-limit bugs or unexpected API overcharges.
- **Cloud-Ready:** Lightweight, single-file codebase that can be deployed instantly to Render, Railway, or Docker with zero friction.

## 🛠️ Tech Stack & Requirements
- Language: Python 3.9+
- Libraries: `pyTelegramBotAPI`, `google-generativeai`
- AI Backbone: Google AI Studio (Gemini API Key)
