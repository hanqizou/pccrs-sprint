# CardSmart — AI Coding Prompt Files

## How to Use

这些 prompt 文件专为 vibe coding 设计，适用于任何 AI coding agent（Codex CLI、Claude Code、Cursor、Copilot 等）。

### Recommended Workflow

1. **每次开始一个 Sprint，先喂入 MASTER.md 作为上下文**

   ```
   # Codex CLI 示例
   codex "Read prompts/MASTER.md and prompts/SPRINT-0-SCAFFOLD.md, then implement all tasks"

   # Claude Code 示例
   claude "Please read prompts/MASTER.md for project context, then follow prompts/SPRINT-0-SCAFFOLD.md to scaffold the project"
   ```
2. **如果单次 prompt 太长，拆分成单个 Task**

   ```
   codex "Read prompts/MASTER.md. Now implement Task 1.2 from prompts/SPRINT-1-AUTH-INGESTION.md — the Registration Page"
   ```
3. **每个 Sprint 结束后，跑 Definition of Done checklist**

   ```
   codex "Check every item in the Definition of Done section of SPRINT-1-AUTH-INGESTION.md. Fix anything that's not done."
   ```

## 文件结构 / File Structure

| File                                    | Purpose                            | When to Use                     |
| --------------------------------------- | ---------------------------------- | ------------------------------- |
| `MASTER.md`                           | 项目全局上下文：架构、Schema、约定 | **每次 session 都要先读** |
| `SPRINT-0-SCAFFOLD.md`                | 项目骨架搭建                       | Week 1                          |
| `SPRINT-1-AUTH-INGESTION.md`          | 注册登录 + 数据导入 + 卡库管理     | Week 2–3                       |
| `SPRINT-2-RECOMMENDATION-ANALYSIS.md` | 推荐引擎 + 分析页面 + 图表         | Week 4–5                       |
| `SPRINT-3-PLAN-HISTORY-ADMIN.md`      | Buy/Sell + 历史 + 报告 + Admin     | Week 6–7                       |
| `SPRINT-4-DEPLOY-POLISH.md`           | 部署 VCM + CI/CD + 安全 + 打磨     | Week 8–9                       |

## 5 Suggested Team Split

| Person      | Primary Responsibility         | Sprint Focus                                         |
| ----------- | ------------------------------ | ---------------------------------------------------- |
| **A** | Backend: Auth + Models         | Sprint 0 (scaffold) + Sprint 1 (auth)                |
| **B** | Backend: Ingestion + FX API    | Sprint 1 (ingestion) + Sprint 2 (API endpoint)       |
| **C** | Backend: Recommendation Engine | Sprint 2 (engine + algorithm)                        |
| **D** | Frontend: Templates + Charts   | Sprint 2 (Plotly charts) + Sprint 3 (all pages)      |
| **E** | Admin + DevOps                 | Sprint 3 (admin) + Sprint 4 (VCM + CI/CD + security) |

> 每个人用自己擅长的 AI tool 独立 vibe coding 自己负责的模块，通过 GitLab merge 合并。

## Core Requirements / Points Target

| Category              | Points        | Sprint                  |
| --------------------- | ------------- | ----------------------- |
| UI (9 screens)        | 300           | 0–3                    |
| Data Integration      | 50            | 1                       |
| Charting              | 75            | 2                       |
| Admin                 | 100           | 3                       |
| Infrastructure        | 50            | 4                       |
| Database (PostgreSQL) | 50            | 4                       |
| CI/CD                 | 40            | 4                       |
| Security              | 25            | 4                       |
| Containerization      | 25            | 4                       |
| Architecture          | 20            | 4                       |
| **Total**       | **735** | **Target ≥ 650** |
