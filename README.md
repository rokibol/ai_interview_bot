# AI-Powered Automated Video Interview System

An automated, low-latency video interview platform built with Python, FastAPI, and LiveKit Multimodal Realtime API. Powered by Google Gemini 3.1 Live Preview, the system dynamically conducts voice interviews, streams context-aware technical questions over WebRTC Data Channels directly to the candidate's screen, and evaluates responses using an asynchronous backend pipeline via Gemini 3.6 Flash to save grading and multilingual feedback into an SQLite database with an integrated client dashboard interface.

## Core Features

* Multimodal Voice Agent: Low-latency bidirectional voice sessions driven by `gemini-3.1-flash-live-preview`.
* Synchronized UI Rendering: WebRTC Data Channels push real-time technical questions directly to the candidate's display screen.
* Automated Device Orchestration: Smart frontend optimization that filters virtual audio devices (like Stereo Mix) and auto-binds standard microphones and headsets.
* Asynchronous Grading Pipeline: Deep evaluation of transcripts after session tear-down via `gemini-3.6-flash`.
* Relational Analytics Database: Structured grading scores, pass/fail status, and bilingual reviews safely preserved inside SQLite.
* Comprehensive Owner Dashboard: Secure HTML5/JavaScript dashboard endpoint displaying historical candidate assessment results.

## System Architecture

* Backend API Layer: FastAPI providing JSON Web Tokens (JWT) for secure LiveKit Room authentication handshakes.
* Real-Time Stream Engine: Asynchronous event-driven Python daemon deploying LiveKit AgentSession architecture.
* Client Interface: Vanilla JavaScript using LiveKit UMD Client SDK with automated browser AudioContext restoration workflows.

## Prerequisites

* Python 3.11 or higher
* LiveKit Cloud Account or Self-Hosted Instance
* Google AI Studio API Key (Gemini)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com
   cd ai_inter_bot
   ```

2. Initialize and activate the Python virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows: venv\Scripts\activate
   ```

3. Upgrade pip and install all project dependencies:
   ```bash
   pip install "livekit-agents[google]" google-genai fastapi uvicorn python-dotenv requests httpx
   ```

4. Configure the Environment Variables:
   Create a `.env` file in the root directory and append the following credentials:
   ```env
   LIVEKIT_URL=your_livekit_cloud_url
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   GOOGLE_API_KEY=your_gemini_api_key
   ```

## Local Development & Execution

1. Fire up the FastAPI Local Token and Dashboard Server:
   ```bash
   python server.py
   ```

2. Launch the LiveKit Multimodal Voice Agent Framework:
   ```bash
   # Standard CLI invocation with Hot-Reload enabled
   lk agent dev
   ```

3. Run the Interview Application:
   Open your preferred browser and traverse to `http://localhost:8000`. Click **Start Interview**, enable hardware permissions, and declare a clear "Hello" to initiate the session.

4. View Analytical Assessment Records:
   Traverse to the private owner endpoint at `http://localhost:8000/dashboard` to review consolidated scoring insights.

## Project Directory Map

* `server.py` - Core FastAPI token handshaker, routing infrastructure, and SQLite connection points.
* `agent.py` - Realtime duplex event listener handling Gemini Live API connections and WebRTC media streams.
* `index.html` - Candidate facing portal managing audio track attachment matrixes and WebRTC data parsing.
* `dashboard.html` - Enterprise result rendering engine structured with localized JS object mapping schemas.
* `.gitignore` - Standard runtime definitions to filter system files, venv cache, and `.env` secrets from git tracking history.

## License

This software utility is preserved under standard proprietary guidelines. All rights reserved.
