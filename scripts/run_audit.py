#!/usr/bin/env python3
"""
Zenfusion Audit Runner — called by GitHub Actions on issue creation.
Reads the issue body for audit type and parameters, runs the appropriate scripts,
and pushes results to GitHub Pages + Google Drive.
"""
import json, os, sys, re, subprocess, time

def parse_issue(issue_body):
    """Parse GitHub issue body for audit parameters."""
    params = {}
    for line in issue_body.split('\n'):
        if '**URL:**' in line or '**Keyword:**' in line or '**Page URL:**' in line or \
           '**Core Keyword:**' in line or '**Client URL:**' in line or '**Target URL:**' in line or \
           '**Max Pages:**' in line or '**Competitor Pages:**' in line:
            key, val = line.split('**', 2)[1].rstrip(':').strip(), line.split('**', 2)[2].strip(': ').strip()
            params[key.lower().replace(' ', '_')] = val
    return params

def run_site_audit(url, limit=100):
    """Run site auditor."""
    cmd = [sys.executable, 'scripts/site_auditor.py', url, '--limit', str(limit)]
    env = os.environ.copy()
    env['SCRAPEOWL_API_KEY'] = env.get('SCRAPEOWL_API_KEY', '')
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
    return result

def run_keyword_audit(keyword, url, limit=30):
    """Run factor engine for keyword audit."""
    # First need SERP data
    from dataforseo_helper import get_serp
    serp_path = f'/tmp/serp_{keyword.replace(" ", "-")}.json'
    serp_data = get_serp(keyword)
    with open(serp_path, 'w') as f:
        json.dump(serp_data, f)
    
    cmd = [sys.executable, 'scripts/factor_engine.py', serp_path, url, '--limit', str(limit)]
    env = os.environ.copy()
    env['SCRAPEOWL_API_KEY'] = env.get('SCRAPEOWL_API_KEY', '')
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
    return result

def main():
    issue_body = os.environ.get('ISSUE_BODY', '')
    issue_number = os.environ.get('ISSUE_NUMBER', '0')
    issue_label = os.environ.get('ISSUE_LABEL', '')
    issue_title = os.environ.get('ISSUE_TITLE', '')
    
    print(f"Processing issue #{issue_number}: {issue_title}")
    print(f"Label: {issue_label}")
    
    params = parse_issue(issue_body)
    print(f"Parsed params: {params}")
    
    if 'site-audit' in issue_label:
        url = params.get('url', '')
        limit = int(params.get('max_pages', 100))
        print(f"\nRunning site audit for {url} (limit: {limit})...")
        result = run_site_audit(url, limit)
        
    elif 'keyword-audit' in issue_label:
        keyword = params.get('keyword', '')
        url = params.get('target_url', '')
        limit = int(params.get('competitor_pages', 30))
        print(f"\nRunning keyword audit for '{keyword}' on {url}...")
        result = run_keyword_audit(keyword, url, limit)
        
    elif 'page-audit' in issue_label:
        url = params.get('page_url', '')
        keyword = params.get('keyword', '')
        print(f"\nRunning page-level audit for {url} on '{keyword}'...")
        # Run both
        site_result = run_site_audit(url, limit=10)
        kw_result = run_keyword_audit(keyword, url, limit=30)
        result = kw_result  # Return keyword result as primary
        
    elif 'aeo-research' in issue_label:
        url = params.get('client_url', '')
        keyword = params.get('core_keyword', '')
        print(f"\nRunning AEO research for {url} on '{keyword}'...")
        print("AEO research requires agent-driven stages — manual execution needed")
        result = None
    else:
        print(f"Unknown label: {issue_label}")
        return
    
    if result:
        print(f"\nExit code: {result.returncode}")
        if result.stdout:
            print(f"Output (last 500 chars):\n{result.stdout[-500:]}")
        if result.stderr:
            print(f"Errors (last 500 chars):\n{result.stderr[-500:]}")
    
    print(f"\n--- Audit complete for issue #{issue_number} ---")

if __name__ == '__main__':
    main()
