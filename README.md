# 🚀 Bacon Maker: The MCP Meta-Orchestrator

Bacon Maker is a Metadata-First Orchestration Layer designed specifically for AI Agents. Using the Model Context Protocol (MCP), it acts as a secure, state-aware bridge between Large Language Models and complex database infrastructures (SQLite, MySQL, Teradata).

## Features
- **State-Aware Execution:** Robust job tracking and recovery.
- **Security First:** Strict `DOMAIN_ROLE` sandboxing for all AI agents.
- **Metadata Driven:** SQL generation via Jinja2 and CEL evaluation.
- **Chaos Resilience:** Integrated Chaos Monkey for failure simulation.

---

## 🚀 Quick Start / Installation

### 1. Environment Setup
Clone the repository and initialize the virtual environment:
```bash
git clone https://github.com/clydewatts1/td_mcp_bacon_maker.git
cd td_mcp_bacon_maker
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies
Install the core orchestration and testing requirements:
```bash
pip install -r requirements.txt
```

### 3. Configure Secrets
Copy the example environment file and add your database credentials:
```bash
cp .env.example .env
# Edit .env with your TERADATA_PWD, MYSQL_PWD, etc.
```

### 4. Launch the MCP Interface
Bacon Maker is an MCP-native server. You can interact with its tools using the **MCP Inspector**:
```bash
npx @modelcontextprotocol/inspector python -m bacon_maker
```

For detailed documentation, see the [Technical Reference Manual](docs/instruction_manual.md) and the [How-To Guide](docs/how_to.md).
