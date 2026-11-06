# Agile Delivery Documentation

Documentation snapshot: **November 6, 2026**.

This folder maps the implemented project to an Agile backlog, user stories, sprint goals, and retrospective actions. The four sprint groupings are reconstructed from the milestone documents, source code, and Git history. They are not records of previously scheduled Scrum ceremonies. No sprint duration, meeting attendance, story-point estimates, or velocity measurements are claimed without recorded evidence.

## Project goal

Help reviewers assess AI-generated answers through traceable evidence, explainable quality scores, batch analytics, and reports.

## Documents

| Document | Purpose |
| --- | --- |
| [Product backlog](product-backlog.md) | Priorities, completion status, dependencies, and implementation evidence |
| [User stories and acceptance criteria](user-stories.md) | User needs and observable conditions for acceptance |
| [Sprint plan and delivery record](sprint-plan.md) | Four milestone-based increments and deployment hardening |
| [Retrospectives](retrospectives.md) | Evidence-based observations, lessons, and follow-up actions |

## Responsibilities

- Repository maintainer: **Arthisri2006**, responsible for source control and release changes.
- Reviewer/mentor: provides requirements and reviews the demonstration; no individual or approval is assumed here.
- Developer: implements stories, checks acceptance criteria, and records known limitations.

These are responsibilities for this project, not a claim that separate people filled each Scrum role.

## Working agreement

For subsequent changes, use the following workflow:

1. Record the requirement as a backlog item with acceptance criteria.
2. Select a small set of items for the next iteration based on dependencies and priority.
3. Move items through **To do → In progress → Review → Done**. Mark an item **Blocked** when an external dependency prevents progress.
4. Implement and validate the change; link the commit and relevant checks.
5. Demonstrate the increment against its acceptance criteria and record feedback.
6. Update the backlog and retrospective actions before the next iteration.

The backlog below is a documentation snapshot, not a synchronized issue tracker or evidence that a board was used historically.

## Definition of Ready

A story has an identifiable user need, clear acceptance criteria, known dependencies, an agreed scope, and a feasible validation approach. Unknown hosting cost or account access is recorded before deployment work begins.

## Definition of Done

- The implemented behavior meets the story's documented scope and acceptance criteria.
- Relevant checks pass, or any remaining limitation is explicitly recorded.
- Errors are handled without fabricating evidence, scores, or success messages.
- Documentation and configuration match the implementation.
- Source changes are committed; secrets, caches, and generated files remain excluded.
- Deployment stories additionally require a live health check and a real user workflow, not only a successful build.

“Done” means the scoped functionality is implemented. It does not imply perfect factual judgement, human benchmark validation, or durable storage on a free hosting instance.

## Submission links

- Repository: https://github.com/Arthisri2006/infosysSpringboard
- Deployed frontend: https://evidence-lab.onrender.com
- Backend health: https://evidence-lab-api.onrender.com/health
- License: [MIT License](../../LICENSE)
