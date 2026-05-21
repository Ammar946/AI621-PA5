# CS5305/CS621 - Programming Assignment 5: Scalable, Enterprise-Grade Agentic AI Game Development

This repository contains the implementation for Programming Assignment 5 (PA5) of the Scalable AI Services / MLOps course.

## Project Overview

The project evolves a Dino Runner development pipeline using a ReAct (Reasoning + Acting) Agent architecture with safety filters, memory management, and LLMOps monitoring.

### Key Features Implemented:
1. **ReAct Agent Architecture**: Transitioned fixed node transitions into autonomous ReAct agents (`Engineer` and `QA`) capable of tool execution using the LangGraph framework.
2. **Specialized Toolset**: Created a custom `CodeInterpreterTool` that handles headless Pygame execution (`SDL_VIDEODRIVER=dummy`) and manages execution timeout fallbacks.
3. **Personally Identifiable Information (PII) Filter**: Integrated `Presidio` to anonymize emails, passwords, and developer API keys, logging redactions to a JSON report.
4. **Human-in-the-Loop (HITL) Workflow**: Enforced mandatory review halts before transitions between nodes and automated feedback routing back to the Architect if the results are unsatisfactory.
5. **Memory and Context Management**: Enabled automatic context summarization of historical designs and QA feedback once threshold token levels are crossed.
6. **MLflow Tracking**: Integrated experiment runs to track agent groundedness scores and execution latencies across multiple iterations.

## Files
* `25280019_pa5.ipynb` / `25280019_pa4.ipynb`: Databricks notebooks containing the LangGraph system execution loop.
* `PA5.pdf`: Assignment specification sheet.
