# Context Garden

A comprehensive knowledge and instruction repository for AI-assisted development in Cursor IDE and GitHub Copilot.

## GitHub Repository

**Remote URL:** `git@github.com:trkhanh/contextGarden.git`

**Access:** [trkhanh/contextGarden on GitHub](https://github.com/trkhanh/contextGarden)

---

## Overview

Context Garden is a collection of AI system instructions, coding guidelines, skills, and project rules designed to enhance pair programming with AI assistants. This repository is linked as an Obsidian folder (Folder 09.Github) for seamless knowledge management and reference.

## Repository Structure

### 📋 Core Components

- **`agents/`** - System prompts and AI instruction sets
  - Core prompt configuration
  - Cursor AI prompting rules
  - System instructions for agentic behavior

- **`skills/`** - Domain-specific expertise packages
  - Rust coding guidelines (50 core rules)
  - Core action book for common patterns
  - Indexed rules and best practices

- **`global-rules/`** - Project-wide standards
  - Cursor official guidelines
  - Custom development practices
  - Project specifications

- **`project-rules/`** - UI/UX and custom project constraints
  - UI/UX best practices
  - Project-specific conventions

- **`features/`** - Feature documentation
  - Mobile/SWeb shared library documentation
  - Backward compatibility scenarios

- **`architecture-planing/`** - System design resources
  - Mermaid diagram templates
  - Architecture decision records

- **`templates/`** - Reusable documentation templates
  - Trace templates for error tracking

- **`_meta/`** - Process documentation
  - Error handling protocol (3-strike rule)
  - Metadata and conventions

- **`claude/`** - Claude-specific configurations
  - Skill evaluation hooks

## Key Features

✅ **Systematic Error Handling** - 3-strike protocol for escalating and resolving issues  
✅ **Rust Best Practices** - 50 core rules for Rust coding standards  
✅ **AI Pair Programming** - Structured prompts for agentic coding assistants  
✅ **Obsidian Integration** - Linked folder for knowledge management  
✅ **Reusable Skills** - Modular, domain-specific guidance packages  

## Usage

This repository serves as:
- A reference for coding standards and guidelines
- A system prompt configuration for Cursor IDE
- An instruction set for GitHub Copilot context
- A knowledge base linked in Obsidian for quick lookup

## Quick Start

1. Clone the repository:
   ```bash
   git clone git@github.com:trkhanh/contextGarden.git
   ```

2. Link to Obsidian:
   - Use "Add folder" in Obsidian settings
   - Point to the cloned directory

3. Reference in your IDE:
   - Import system instructions into Cursor
   - Apply skills and guidelines to your project

## Obsidian Customization

### Directory Path Mapping

Customize how this folder appears in your Obsidian vault:

#### Option 1: Linked Folder with Custom Display Name

1. Open Obsidian Settings → Linked Data → Excluded Files
2. Add folder path: `/home/kane/Workspaces/contextGarden`
3. Create a symlink in your vault:
   ```bash
   ln -s /home/kane/Workspaces/contextGarden ~/Obsidian/Vault/09.Github
   ```
4. Result: Folder appears as `09.Github` in your vault

#### Option 2: Using .obsidian/folders.json

Edit your vault's `.obsidian/folders.json` to create custom mappings:
```json
{
  "linked-folders": [
    {
      "path": "/home/kane/Workspaces/contextGarden",
      "displayName": "09.Github",
      "targetPath": "github/"
    }
  ]
}
```

#### Option 3: Create Alias Notes

In a note at the vault root:
```markdown
# Context Garden Reference
![[09.Github/agents/00-system-instruction.md]]
![[09.Github/skills/coding-guidelines/SKILL.md]]
```
Then access via `[[09.Github]]` reference throughout your vault.

#### Option 4: Configure Obsidian URI Handler

Use Obsidian URI to auto-navigate:
```
obsidian://open?path=/home/kane/Workspaces/contextGarden/agents/
```

### Best Practices

- **Use consistent naming**: Keep `09.Github` as your folder identifier for easy reference
- **Version control**: Commit path configuration changes to git
- **Cross-reference**: Link frequently-used skills in your vault's index
- **Sync aliases**: Keep display names synchronized with vault structure

---

**Last Updated:** April 2026  
**Maintained By:** trkhanh