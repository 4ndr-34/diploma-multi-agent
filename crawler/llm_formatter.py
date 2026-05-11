from typing import Dict, Optional, List


class LLMFormatter:
    def __init__(self, max_files_in_summary: int = 20, max_diffs: int = 5):
        """
        Initialize LLM formatter

        Args:
            max_files_in_summary: Maximum files to show in summary
            max_diffs: Maximum full diffs to include
        """
        self.max_files_in_summary = max_files_in_summary
        self.max_diffs = max_diffs

    def format_for_llm(self, pr_payload: Dict, include_full_diff: bool = False,
                       include_metadata: bool = True) -> str:
        """
        Format PR data into a prompt-friendly structure for LLM analysis

        Args:
            pr_payload: PR data from crawler
            include_full_diff: Whether to include actual code diffs
            include_metadata: Whether to include metadata section
        """
        if not pr_payload:
            return "Error: No PR data provided"

        # Build the prompt sections
        sections = []

        if include_metadata:
            sections.append(self._build_metadata_section(pr_payload))

        sections.append(self._build_files_section(pr_payload))

        if include_full_diff and not pr_payload.get("truncated", False):
            sections.append(self._build_diffs_section(pr_payload))
        else:
            sections.append(self._build_truncated_notice(pr_payload))

        sections.append(self._build_analysis_request())

        return "\n\n".join(sections)

    def _build_metadata_section(self, pr: Dict) -> str:
        """Build metadata section of the prompt"""
        lines = [
            "# Pull Request Analysis Request",
            "",
            "## Metadata",
            f"- **Repository:** {pr['repo']}",
            f"- **PR #{pr['id']}:** {pr['title']}",
            f"- **Author:** @{pr['author']}",
            f"- **State:** {pr.get('state', 'unknown')}",
            f"- **Created:** {pr.get('created_at', 'unknown')}",
            f"- **Labels:** {', '.join(pr.get('labels', [])) or 'none'}",
            f"- **Changes:** +{pr.get('additions', 0)} / -{pr.get('deletions', 0)} lines",
            f"- **Files changed:** {len(pr.get('files', []))}",
            f"- **Comments:** {pr.get('comments_count', 0)}",
            f"- **Review Comments:** {pr.get('review_comments_count', 0)}",
        ]

        if pr.get('body_preview'):
            lines.append(f"- **Description preview:** {pr['body_preview']}")

        return "\n".join(lines)

    def _build_files_section(self, pr: Dict) -> str:
        """Build files summary section"""
        files = pr.get('files', [])
        if not files:
            return "## Files Changed\n\nNo files were changed in this PR."

        # Create summary table
        summary_lines = [
            "## Files Changed",
            "",
            "| Status | Filename | Additions | Deletions | Changes |",
            "|--------|----------|-----------|-----------|---------|"
        ]

        for f in files[:self.max_files_in_summary]:
            status_emoji = {
                "added": "➕",
                "modified": "✏️",
                "removed": "❌",
                "renamed": "🔄"
            }.get(f['status'], "📄")

            summary_lines.append(
                f"| {status_emoji} {f['status']} | `{f['filename']}` | +{f.get('additions', 0)} | -{f.get('deletions', 0)} | {f.get('changes', 0)} |"
            )

        if len(files) > self.max_files_in_summary:
            summary_lines.append(f"\n*... and {len(files) - self.max_files_in_summary} more files*")

        return "\n".join(summary_lines)

    def _build_diffs_section(self, pr: Dict) -> str:
        """Build code diffs section"""
        files = pr.get('files', [])
        diff_files = [f for f in files if f.get('patch')][:self.max_diffs]

        if not diff_files:
            return "## Code Changes\n\nNo code diffs available (binary files or non-code changes)"

        sections = ["## Code Changes"]

        for f in diff_files:
            sections.append(f"### `{f['filename']}`")
            sections.append(f"```diff\n{f['patch']}\n```")

        remaining_files = len([f for f in files if f.get('patch')]) - len(diff_files)
        if remaining_files > 0:
            sections.append(f"\n*... and {remaining_files} more files with changes*")

        return "\n".join(sections)

    def _build_truncated_notice(self, pr: Dict) -> str:
        """Build notice for truncated PRs"""
        if pr.get('truncated'):
            return "## ⚠️ Note\n\nThis PR data was truncated due to size limitations. Full diffs are not included in this analysis."
        return "## Code Changes\n\nFull diffs omitted due to size. Refer to the files summary above."

    def _build_analysis_request(self) -> str:
        """Build the analysis request section"""
        return """## Analysis Request

Please analyze this pull request and provide:

### 1. Summary
- What does this PR aim to achieve?
- What are the main changes?

### 2. Code Quality Review
- Code organization and structure
- Naming conventions
- Comments and documentation
- Potential code smells

### 3. Potential Issues
- Logical bugs
- Edge cases not handled
- Performance concerns
- Security vulnerabilities
- Compatibility issues

### 4. Testing Assessment
- Are there tests?
- What should be tested?

### 5. Specific Recommendations
- Immediate blocking issues (if any)
- Suggested improvements
- Best practice violations

### 6. Overall Assessment
- **Risk Level:** (Low/Medium/High)
- **Readiness:** (Ready to merge / Needs changes / Needs review)
- **Confidence Score:** (1-10)

Please structure your response with clear headings and bullet points."""

    def format_summary_for_llm(self, pr_payload: Dict) -> str:
        """Create a minimal prompt for quick summaries"""
        return f"""Analyze this PR briefly:

PR #{pr_payload['id']}: {pr_payload['title']}
Author: @{pr_payload['author']}
Changes: +{pr_payload.get('additions', 0)}/-{pr_payload.get('deletions', 0)} lines in {len(pr_payload.get('files', []))} files

Give a 2-3 sentence summary of what this PR does and any immediate red flags."""