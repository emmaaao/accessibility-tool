from datetime import datetime


class AccessibilityReporter:
    #HTML report generator for accessibility analysis

    def generate_report(self, results: dict) -> str:
        """Generate HTML report from analysis results"""
        url = results.get('url', 'Unknown')
        axe = results.get('axe_results', {})
        week2 = results.get('week2', {})
        ai = results.get('ai_results')

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Report</title>
    <style>
        body {{ font-family: system-ui, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .container {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .card {{ background: #f8f9fa; padding: 20px; border-radius: 6px; border-left: 4px solid #667eea; }}
        .card h3 {{ margin: 0 0 10px 0; font-size: 0.9em; color: #666; }}
        .card .value {{ font-size: 2em; font-weight: bold; color: #333; }}
        .issue {{ background: white; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; }}
        .issue:hover {{ box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: bold; }}
        .critical {{ background: #dc3545; color: white; }}
        .serious {{ background: #fd7e14; color: white; }}
        .moderate {{ background: #ffc107; color: #333; }}
        .minor {{ background: #28a745; color: white; }}
        .recommendation {{ background: #d4edda; padding: 10px; margin-top: 10px; border-left: 4px solid #28a745; border-radius: 4px; }}
        .ai-insight {{ background: #fff3cd; padding: 10px; margin-top: 10px; border-left: 4px solid #ffc107; border-radius: 4px; }}
        .wcag-link {{ display: inline-block; background: #e7f3ff; color: #0066cc; padding: 4px 10px; border-radius: 4px; text-decoration: none; margin: 5px 5px 0 0; }}
        .wcag-link:hover {{ background: #cce5ff; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1> Accessibility Analysis Report</h1>
        <p><strong>URL:</strong> {url}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        {self._summary_section(axe, week2, ai)}
        {self._axe_section(axe)}
        {self._rule_section(week2)}
        {self._ai_section(ai)}
        {self._actions_section()}
    </div>
</body>
</html>"""
        return html

    def _summary_section(self, axe, week2, ai):
        """Summary"""
        violations = len(axe.get('violations', []))
        link_issues = len(week2.get('links', []))
        img_issues = len(week2.get('images', []))
        total = violations + link_issues + img_issues

        ai_count = 0
        if ai and 'ai_advice' in ai:
            advice = ai['ai_advice']
            ai_count = len(advice.get('links', [])) + len(advice.get('images', []))

        return f"""
        <h2>Summary</h2>
        <div class="summary">
            <div class="card">
                <h3>Total Issues</h3>
                <div class="value">{total}</div>
            </div>
            <div class="card">
                <h3>Technical (Axe)</h3>
                <div class="value">{violations}</div>
            </div>
            <div class="card">
                <h3>Semantic (Rules)</h3>
                <div class="value">{link_issues + img_issues}</div>
            </div>
            <div class="card">
                <h3>AI Analyzed</h3>
                <div class="value">{ai_count}</div>
            </div>
        </div>
        """

    def _axe_section(self, axe):
        """Axe-core violations"""
        violations = axe.get('violations', [])
        if not violations:
            return '<h2>Technical Issues (Axe-core)</h2><p>No violations found!</p>'

        html = '<h2>Technical Issues (Axe-core)</h2>'
        for v in violations[:10]:  # Show first 10
            impact = v.get('impact', 'moderate')
            html += f"""
            <div class="issue">
                <strong>{v.get('id', 'Unknown').replace('-', ' ').title()}</strong>
                <span class="badge {impact}">{impact}</span>
                <p>{v.get('description', '')}</p>
                <p><strong>Affected:</strong> {len(v.get('nodes', []))} element(s)</p>
                <a href="{v.get('helpUrl', '#')}" class="wcag-link" target="_blank">Learn More</a>
            </div>
            """
        return html

    def _rule_section(self, week2):
        """Rule-based findings"""
        links = week2.get('links', [])
        images = week2.get('images', [])

        if not links and not images:
            return '<h2>Semantic Issues (Rules)</h2><p>No issues found!</p>'

        html = '<h2>Semantic Issues (Rule-Based)</h2>'

        # Link issues
        if links:
            html += '<h3>Links</h3>'
            for issue in links[:10]:
                sev = issue.get('severity', 'moderate')
                html += f"""
                <div class="issue">
                    <strong>Vague Link Text</strong>
                    <span class="badge {sev}">{sev}</span>
                    <p>Link text doesn't clearly describe destination.</p>
                    <a href="https://www.w3.org/WAI/WCAG21/Understanding/link-purpose-in-context.html" 
                       class="wcag-link" target="_blank">WCAG 2.4.4 (A)</a>
                    <div class="recommendation">
                        <strong>Fix:</strong> Use descriptive text. Avoid "click here", "read more".
                    </div>
                </div>
                """

        # Image issues
        if images:
            html += '<h3>Images</h3>'
            for issue in images[:10]:
                sev = issue.get('severity', 'moderate')
                issue_type = issue.get('issue', 'alt_issue')

                desc = {
                    'missing_alt': 'Image missing alt text',
                    'generic_alt': 'Alt text is generic ("image", "photo")',
                    'weak_alt': 'Alt text too brief'
                }.get(issue_type, 'Alt text issue')

                html += f"""
                <div class="issue">
                    <strong>{desc}</strong>
                    <span class="badge {sev}">{sev}</span>
                    <a href="https://www.w3.org/WAI/WCAG21/Understanding/non-text-content.html" 
                       class="wcag-link" target="_blank">WCAG 1.1.1 (A)</a>
                    <div class="recommendation">
                        <strong>Fix:</strong> Add meaningful alt text describing the image.
                    </div>
                </div>
                """

        return html

    def _ai_section(self, ai):
        """AI findings"""
        if not ai or 'ai_advice' not in ai:
            return ''

        advice = ai['ai_advice']
        links = advice.get('links', [])
        images = advice.get('images', [])

        html = '<h2>AI Contextual Analysis</h2>'
        html += '<p>Claude AI analyzed these elements for context and meaning:</p>'

        # AI link analysis
        if links:
            html += '<h3>Links</h3>'
            for item in links[:5]:
                link = item.get('link', {})
                analysis = item.get('ai_analysis', {})

                if analysis.get('is_accessible') == False or analysis.get('issue'):
                    sev = analysis.get('severity', 'moderate')
                    html += f"""
                    <div class="issue">
                        <strong>"{link.get('text', 'Unknown')}"</strong>
                        <span class="badge {sev}">{sev}</span>
                        <p><strong>Issue:</strong> {analysis.get('issue', 'Concern identified')}</p>
                        <p><strong>URL:</strong> <code>{link.get('href', 'N/A')[:60]}...</code></p>
                        <div class="recommendation">
                            <strong>AI Suggests:</strong> {analysis.get('recommendation', 'Improve clarity')}
                        </div>
                        {f'<div class="ai-insight"><strong>Why:</strong> {analysis.get("reasoning", "")}</div>' if analysis.get('reasoning') else ''}
                    </div>
                    """

        # AI image analysis
        if images:
            html += '<h3>Images</h3>'
            for item in images[:5]:
                img = item.get('image', {})
                analysis = item.get('ai_analysis', {})

                if analysis.get('is_accessible') == False or analysis.get('issue'):
                    sev = analysis.get('severity', 'moderate')
                    html += f"""
                    <div class="issue">
                        <strong>Alt: "{img.get('alt', '(missing)')}"</strong>
                        <span class="badge {sev}">{sev}</span>
                        <p><strong>Issue:</strong> {analysis.get('issue', 'Alt text needs improvement')}</p>
                        <div class="recommendation">
                            <strong>AI Suggests:</strong> {analysis.get('recommendation', 'Add descriptive alt')}
                        </div>
                    </div>
                    """

        return html

    def _actions_section(self):
        """Actions"""
        return """
        <h2>Actions</h2>
        <ol>
            <li><strong>Fix critical technical issues</strong> - Start with Axe-core "critical" and "serious" items</li>
            <li><strong>Improve link text</strong> - Make all links descriptive</li>
            <li><strong>Add missing alt text</strong> - Describe all images meaningfully</li>
            <li><strong>Review AI suggestions</strong> - Consider contextual improvements</li>
            <li><strong>Test with screen readers</strong> - Validate changes with assistive tech</li>
        </ol>
        <p style="margin-top: 20px; color: #666; font-size: 0.9em;">
            Reference: <a href="https://www.w3.org/WAI/WCAG21/quickref/" target="_blank">WCAG 2.1 Quick Reference</a>
        </p>
        """

    def save_report(self, html: str, filename: str = None) -> str:
        """Save report to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.html"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

        return filename