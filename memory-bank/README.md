# GPSE Memory Bank

## Purpose
This memory bank serves as the persistent context and documentation for the Geopolitical Grand Strategy Engine (GPSE) project. It ensures continuity across development sessions and maintains the project's strategic integrity.

## Structure

### Core Documentation Files

1. **`projectbrief.md`**
   - Project mission and identity
   - Core objectives and principles
   - Target users and value proposition

2. **`productContext.md`**
   - Problem statement and solution approach
   - User journey and workflows
   - System boundaries and constraints

3. **`systemPatterns.md`**
   - Architecture and design patterns
   - CrewAI agent specifications
   - Data flow and naming conventions
   - Integration points

4. **`techContext.md`**
   - Technology stack details
   - API specifications and keys
   - Development environment setup
   - Security and performance considerations

5. **`activeContext.md`**
   - Current development phase
   - Recent activities and decisions
   - Open questions and blockers
   - Next session priorities

6. **`progress.md`**
   - Component completion status
   - Known issues and technical debt
   - Testing status
   - Milestones and success metrics

## Usage Guidelines

### For Development Sessions
1. **Always start by reading all memory bank files** to understand current state
2. **Update `activeContext.md`** with any significant work done
3. **Update `progress.md`** when completing features or identifying issues
4. **Modify other files** when making architectural decisions or changes

### For New Features
- Document design decisions in `systemPatterns.md`
- Update technical requirements in `techContext.md`
- Track implementation progress in `progress.md`

### For Maintenance
- Keep `activeContext.md` current with latest activities
- Review and update `progress.md` regularly
- Archive outdated information appropriately

## Key Principles
- **Single Source of Truth**: This memory bank is the authoritative source for project context
- **Living Documentation**: Update files as the project evolves
- **Continuity**: Enables seamless handoffs between sessions
- **Clarity**: Write for your future self or other developers

## Quick Reference

### Current Status (June 2, 2025)
- **Phase**: Foundation Setup
- **Completed**: ChromaDB integration, utilities, memory bank
- **Next**: CrewAI implementation, API integrations
- **Blockers**: None

### Key Files in Project
- `db_manager.py` - ChromaDB interface (functional)
- `gpse_tools.py` - Utility functions (just created)
- `strategy_analyses/` - Generated analysis documents
- `strategy_db_chroma/` - Vector database storage

### Next Steps
1. Install remaining dependencies
2. Create CrewAI agent definitions
3. Implement API integrations
4. Build main orchestration script

---
*Remember: Always read the memory bank before starting work!*
