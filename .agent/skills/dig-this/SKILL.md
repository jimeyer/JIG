---
name: dig-this
description: Create DIG deliberation documents from conversation context. Triggers on "dig this", "dig that", or "dig it".
---

# dig-this

Create DIG (Deliberation Insight Graph) documents to capture reasoning and decisions.

## Trigger

User says "dig this", "dig that", or "dig it" with optional modifiers:
- `as <type>` - specify document type
- `: "<title>"` - specify document title

## Examples

- "dig this" - capture current conversation context
- "dig that as exploration" - create exploration document
- "dig this: 'Auth Discussion'" - create document with specific title

## Procedure

1. **Parse trigger phrase** for optional modifiers
2. **Infer missing values** from conversation:
   - **Type**: Based on conversation mode (see Type Inference below)
   - **Title**: From key topic discussed
   - **Parent**: From [[references]] mentioned, or null if root
3. **Determine document number** from existing files (D001, D002, etc.)
4. **Create document** using digy new:
   ```bash
   digy new <type> <title> \
     --parent "[[...]]" \
     --prompt "<conversation excerpt>" \
     --update-parent <<'EOF'
   <synthesized body>
   EOF
   ```
5. **Validate** with `digy validate <path>`
6. **Report** success with file path

## Type Inference Guide

| Conversation Mode | Inferred Type |
|-------------------|---------------|
| Open-ended what-ifs, brainstorming | exploration |
| Problem/opportunity definition | scope |
| Implementation planning | jigplan |
| Detailed task breakdown | plan |
| Running notes during work | journal |
| Work unit completion | wu |
| Lessons learned, post-hoc | retrospective |

## Document Types

- **exploration**: Divergent thinking, what-ifs, brainstorming
- **scope**: Convergent problem definition
- **jigplan**: Alignment with JIG specifications
- **plan**: Implementation breakdown with work units
- **journal**: Running notes during execution
- **wu**: Work unit completion record
- **retrospective**: Post-hoc lessons learned

## Frontmatter Schema

Required fields in every DIG document:
- `type`: Document type (see above)
- `status`: active | parked | implemented | abandoned | superseded
- `created`: Unix epoch seconds
- `created_human`: Human-readable datetime
- `parent`: null or [[wiki-link]]
- `children`: Array of [[wiki-links]]

Optional:
- `prompt`: The triggering prompt (multiline string)
