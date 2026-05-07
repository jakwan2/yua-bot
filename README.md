# 🌸 Yua AI - Advanced Discord Chatbot

Yua is a highly interactive, personality-driven Discord chatbot built with Python and powered by Google's Gemini Pro API. She is designed to be a smart companion with a unique, supportive, and engaging personality.

## 🚀 Key Features

- **Multi-API Key Rotation:** Implements proprietary logic to switch between multiple Gemini API keys to ensure high availability and bypass rate limits.
- **Dynamic Model Fallback:** Automatically switches between latest Gemini Flash models to maintain system stability.
- **Custom Personality Engine:** Features a carefully crafted system prompt that provides a consistent and engaging user experience.
- **Intelligent Error Handling:** Equipped with custom fallback triggers to inform users when the system is under heavy load without crashing.
- **Rate-Limit Management:** Optimized user-level cooldowns to ensure fair usage and system longevity.

## 🛠️ Technical Stack

- **Language:** Python
- **Core Library:** `discord.py`
- **AI Engine:** Google Gemini API
- **Platform:** Replit

## 🧠 The "Gomenasai" Logic
One of the core technical highlights is the resilience layer. If the API hits a "429 Resource Exhausted" error across all rotation keys, the bot gracefully handles the exception and sends a pre-defined personality-matched notification to the user.

## 👤 Developer
- **Name:**  Drift
- **Focus:** AI Development & Digital Marketing
- **Goal:** Designing resilient AI systems and exploring automated marketing strategies.

---
