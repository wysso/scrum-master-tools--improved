# ScrumMaster Tools - User Guide

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [Tools Overview](#tools-overview)
- [Detailed Tool Guides](#detailed-tool-guides)
- [Interpreting Results](#interpreting-results)
- [Best Practices for Scrum Masters](#best-practices-for-scrum-masters)
- [Use Cases & Scenarios](#use-cases--scenarios)

---

## Introduction

### What is ScrumMaster Tools (SMT)?

ScrumMaster Tools is a comprehensive analysis suite designed specifically for Scrum Masters, Product Owners, and development teams working with Jira. It transforms raw Jira data into actionable insights that help improve team performance, sprint planning, and development processes.

### Who Should Use SMT?

**Primary Users:**
- **Scrum Masters** - Sprint analysis, team performance insights, retrospective data
- **Product Owners** - Sprint completion analysis, planning effectiveness
- **Team Leads** - Developer performance trends, workload distribution
- **Agile Coaches** - Process improvement insights, team maturity assessment

**Secondary Users:**
- **Developers** - Personal performance tracking, focus rate analysis
- **Management** - High-level team productivity insights
- **QA Teams** - Defect analysis, testing workload assessment

### Key Benefits

✅ **Data-Driven Decisions** - Replace gut feelings with concrete metrics
✅ **Sprint Retrospectives** - Rich data for meaningful discussions
✅ **Planning Improvement** - Historical data for better sprint planning
✅ **Team Development** - Identify support and training opportunities
✅ **Process Optimization** - Find bottlenecks and improvement areas
✅ **Stakeholder Communication** - Clear metrics for reporting

---

## Getting Started

### Your First Analysis in 10 Minutes

Follow this step-by-step guide to run your first analysis:

#### Step 1: Launch SMT
```
# Windows
Double-click: ScrumMaster Tools.bat

# macOS
Double-click: ScrumMaster Tools.command

# Linux/Command Line
python smt.py
```

#### Step 2: SMT Main Menu
```
🚀 ScrumMaster Tools v2.11.1
===============================================

📊 MAIN ANALYSIS TOOLS:
   1. Sprint Completion Analysis
   2. Worklog Summary
   3. Anomaly Detector
   4. Planning Tool
   5. Issue Type Summary
   6. Developer Performance

🔧 HELPER TOOLS:
   7. Connection Test
   8. Projects Lister
   [...]

📝 Choose tool (1-15): _
```

#### Step 3: First-Time Setup
**Recommended**: Start with **Connection Test (7)** to verify your setup:

```
🔧 Connection Test
==================================================

✅ Testing connection to Jira...
✅ Connected successfully!
✅ User: John Doe (john.doe@company.com)
✅ Permissions: Verified
✅ Custom fields: Configured correctly

🎯 Connection test completed successfully!
```

#### Step 4: Run Sprint Completion Analysis
Choose **Sprint Completion (1)** for your first analysis:

```
🎯 Sprint Completion Analysis
==================================================

📝 Enter project name or key (e.g. TMM or APIM): MYPROJ

🎯 Working with project: MYPROJ

📋 Checking boards for project MYPROJ...
✅ Using board: MYPROJ Scrum Board

📅 Fetching sprints from board 'MYPROJ Scrum Board'...
✅ Found 12 sprints:

   1. ⚪ MYPROJ Sprint 25 (FUTURE)
   2. 🟢 MYPROJ Sprint 24 (ACTIVE)
   3. 🔵 MYPROJ Sprint 23 (CLOSED)
   4. 🔵 MYPROJ Sprint 22 (CLOSED)
   [...]

📝 Choose sprint number: 3
```

#### Step 5: Configure Exclusions
SMT will ask about exclusions (filters for your analysis):

```
🔧 EXCLUSIONS MANAGEMENT
==================================================

Current project: MYPROJ
Available exclusions for this project:

   1. ⚙️ Configure exclusions interactively
   2. 📋 Show current exclusions
   3. ➕ Add temporary exclusion
   4. ➖ Remove temporary exclusion
   5. ✅ Continue with current settings

📝 Choose option (1-5): 5
```

**First-time tip**: Choose **5** to continue with default settings.

#### Step 6: Review Results
SMT will analyze your sprint and show results:

```
📊 SPRINT COMPLETION ANALYSIS RESULTS
==================================================
Project: MYPROJ
Sprint: MYPROJ Sprint 23 (2024-01-01 to 2024-01-14)

📈 KEY METRICS:
   • Total Issues Analyzed: 23
   • Completed During Sprint: 18 (78%)
   • Completed After Sprint: 3 (13%)
   • Not Completed: 2 (9%)

📊 BY CATEGORY:
   • Backend: 12 issues (67% completion)
   • Frontend: 8 issues (88% completion)
   • DevOps: 3 issues (100% completion)

📁 Report saved: output/reports/MYPROJ_sprint_completion_20240118_1430.csv

🎯 Analysis completed successfully!
```

**Congratulations!** You've run your first SMT analysis. The CSV file contains detailed data you can analyze further.

---

## Tools Overview

### Main Analysis Tools

#### 🎯 1. Sprint Completion Analysis
**Purpose**: Analyze what was actually completed during vs after sprint
**Best for**: Sprint retrospectives, planning accuracy assessment
**Key insight**: "Did we deliver what we committed to?"

#### ⏰ 2. Worklog Summary
**Purpose**: Time logging patterns and focus rate analysis
**Best for**: Productivity assessment, interruption analysis
**Key insight**: "How focused was our team during the sprint?"

#### 🔍 3. Anomaly Detector
**Purpose**: Statistical detection of unusual patterns or outliers
**Best for**: Quality assurance, risk identification
**Key insight**: "What needs our attention?"

#### 📋 4. Planning Tool
**Purpose**: Multi-sprint planning effectiveness analysis
**Best for**: Improving sprint planning meetings
**Key insight**: "Are we getting better at planning?"

#### 📊 5. Issue Type Summary
**Purpose**: Work distribution analysis by issue types
**Best for**: Capacity planning, workflow optimization
**Key insight**: "What type of work do we actually do?"

#### 👥 6. Developer Performance
**Purpose**: Individual and team performance insights
**Best for**: 1:1s, team development, coaching
**Key insight**: "How can we support our team members?"

### Helper Tools

#### 🔧 7. Connection Test
**Purpose**: Verify Jira connectivity and configuration
**When to use**: First setup, troubleshooting, after Jira changes

#### 📂 8. Projects Lister
**Purpose**: Discover available Jira projects
**When to use**: Finding correct project keys, permission verification

#### 🏷️ 9. Label Updater
**Purpose**: Bulk update issue labels based on patterns
**When to use**: Data cleanup, standardization, migration

#### 🧩 10. Components Updater (v2.6.0)
**Purpose**: JQL-based bulk component updates
**When to use**: Component restructuring, bulk organization

---

## Detailed Tool Guides

### 🎯 Sprint Completion Analysis

#### What It Does
Analyzes each issue in your sprint to determine:
- Was it completed during the sprint timeframe?
- Was it completed after the sprint ended?
- Is it still incomplete?
- Who completed it and when?

#### When to Use
- **Before Sprint Retrospectives** - Gather concrete data about what was delivered
- **Planning Reviews** - Understand historical completion patterns
- **Process Improvement** - Identify why scope changes happen
- **Stakeholder Updates** - Provide accurate delivery metrics

#### Understanding the Results

**Sample Output:**
```
📈 KEY METRICS:
   • Total Issues Analyzed: 23
   • Completed During Sprint: 18 (78%)
   • Completed After Sprint: 3 (13%)
   • Not Completed: 2 (9%)

📊 BY CATEGORY:
   • Backend: 12 issues (67% completion)
   • Frontend: 8 issues (88% completion)
   • DevOps: 3 issues (100% completion)
```

**What This Tells You:**
- **78% completion during sprint** - Good delivery rate, but room for improvement
- **13% completed after** - Some work spilled over, investigate why
- **Frontend performing better** - Backend might need support or have complexity issues
- **DevOps 100%** - Small sample size, but good completion rate

#### Actionable Insights

**If completion rate is low (<70%):**
- Review sprint planning - are you over-committing?
- Check for external dependencies or blockers
- Assess story sizing accuracy
- Consider team capacity changes

**If many items complete after sprint:**
- Look for pattern in types of work that spills over
- Review definition of done
- Check for scope creep during sprint
- Assess estimation accuracy

**Category imbalances:**
- High-performing categories: What's working well? Can you replicate it?
- Low-performing categories: Need more resources? Different approach?

### ⏰ Worklog Summary

#### What It Does
Analyzes time logging patterns to understand:
- How much time was logged during the sprint period
- Focus Rate - how concentrated the work effort was
- Time distribution across different types of work
- Individual developer contribution patterns

#### Understanding Focus Rate
**Focus Rate** = (Time on Primary Tasks / Total Time) × 100

**Focus Rate Guide:**
- **90%+** - Excellent focus, minimal task switching
- **80-89%** - Good focus, normal level of interruptions
- **70-79%** - Moderate focus, some multitasking
- **60-69%** - Low focus, significant interruptions
- **<60%** - Very fragmented work, investigate causes

#### Sample Results Analysis

```
📊 WORKLOG SUMMARY RESULTS
==================================================
Total Time Logged: 284.5 hours
Average Focus Rate: 73%
Developers Analyzed: 6

👥 BY DEVELOPER:
   • Alice Johnson: 52.5h (Focus: 85%)
   • Bob Smith: 48.0h (Focus: 67%)
   • Carol Davis: 45.5h (Focus: 78%)
   [...]

📊 BY CATEGORY:
   • Backend Development: 156h (55%)
   • Frontend Development: 89h (31%)
   • DevOps/Infrastructure: 28h (10%)
   • Bug Fixes: 11.5h (4%)
```

#### Actionable Insights

**High Focus Rate (85%+):**
- ✅ Great! Minimal interruptions, good flow state
- 🔍 Check: Are they getting adequate support/collaboration?
- 💡 Consider: Pair them with lower-focus teammates as mentors

**Low Focus Rate (<65%):**
- 🔍 Investigate: Too many meetings? Context switching? Support requests?
- 💡 Actions: Block focus time, reduce interruptions, better task batching
- 🤝 Support: Pair programming, knowledge sharing to reduce individual load

**Time Distribution Insights:**
- **High bug fix %** - Quality issues, consider prevention strategies
- **Low feature development %** - Too much maintenance work?
- **Uneven developer hours** - Capacity planning or availability issues?

### 🔍 Anomaly Detector

#### What It Does
Uses statistical analysis to automatically identify:
- Issues with unusual original estimate (h)s vs time logged ratios
- Tasks completed unusually early or late in the sprint
- Developers performing significantly different from team average
- Work distribution patterns that deviate from normal

#### Types of Anomalies

**1. Estimation Anomalies**
```
⚠️  ESTIMATION ANOMALY DETECTED
Issue: PROJ-123 "Implement user authentication"
Estimated: 5 original estimate (h)s
Actual time: 2.5 hours
Expected time: 15-25 hours
Severity: HIGH
```
**Possible causes**: Over-estimation, reused existing solution, pair programming efficiency

**2. Completion Time Anomalies**
```
⚠️  COMPLETION TIME ANOMALY DETECTED
Issue: PROJ-456 "Database migration"
Completed: Day 1 of 14-day sprint
Expected: Day 7-10 based on complexity
Severity: MEDIUM
```
**Possible causes**: Dependencies resolved early, simpler than expected, pre-work done

**3. Developer Performance Anomalies**
```
⚠️  DEVELOPER PERFORMANCE ANOMALY DETECTED
Developer: John Doe
Sprint velocity: 23 original estimate (h)s
Team average: 15 original estimate (h)s
Standard deviation: +2.1σ
Severity: LOW
```
**Possible causes**: Taking larger tasks, very productive period, measurement error

#### How to Respond to Anomalies

**Don't assume problems!** Anomalies can be:
- ✅ **Positive** - Efficiency gains, process improvements, learning
- ⚠️ **Neutral** - Normal variation, measurement quirks
- ❌ **Negative** - Problems requiring attention

**Investigation approach:**
1. **Review context** - What else was happening during this period?
2. **Talk to people** - Get the human story behind the numbers
3. **Look for patterns** - Is this a one-off or recurring?
4. **Consider actions** - What, if anything, should change?

### 📋 Planning Tool

#### What It Does
Compares planned vs actual outcomes across multiple sprints to assess:
- Sprint commitment accuracy over time
- Velocity consistency and trends
- Planning improvement or degradation patterns
- Team capacity utilization effectiveness

#### Multi-Sprint Analysis
This tool shines when analyzing 3+ sprints to identify trends:

```
📊 PLANNING EFFECTIVENESS TRENDS (Last 6 Sprints)
==================================================

Sprint Commitment Accuracy:
Sprint 18: 67% completion ⬇️
Sprint 19: 72% completion ➡️
Sprint 20: 78% completion ⬆️
Sprint 21: 81% completion ⬆️
Sprint 22: 79% completion ➡️
Sprint 23: 83% completion ⬆️

Trend: 📈 IMPROVING (+16% over 6 sprints)

Velocity Consistency:
Average: 42 original estimate (h)s
Standard deviation: 6.2 points
Coefficient of variation: 14.8% (GOOD)
```

#### Interpreting Planning Data

**Commitment Accuracy Trends:**
- **Improving (📈)** - Team is learning, planning getting better
- **Declining (📉)** - Need attention: over-committing? External factors?
- **Stable High (➡️ 80%+)** - Great! Mature planning process
- **Stable Low (➡️ <70%)** - Systematic issues to address

**Velocity Consistency:**
- **Low variation (<15%)** - Predictable team, good for planning
- **Medium variation (15-25%)** - Normal, manageable fluctuation
- **High variation (>25%)** - Unpredictable, investigate causes

#### Actionable Insights for Planning

**For Improving Teams:**
- ✅ Celebrate progress! Share what's working
- 🔍 Document successful planning practices
- 📚 Continue learning and refining process

**For Declining Performance:**
- 🔍 Recent changes: New team members? Different work types? External pressures?
- 📋 Review planning process: Estimation methods, capacity calculation
- 🤝 Team retrospective: What's making planning harder?

### 📊 Issue Type Summary

#### What It Does
Breaks down your sprint work by issue types (Stories, Bugs, Tasks, etc.) to show:
- Distribution of different work types
- Estimation accuracy by work type
- Time allocation patterns
- Category-based performance metrics

#### Sample Analysis

```
📊 ISSUE TYPE DISTRIBUTION
==================================================

📈 BY COUNT:
   • Story: 15 issues (65%)
   • Bug: 5 issues (22%)
   • Task: 3 issues (13%)

📊 BY original estimate (h)S:
   • Story: 89 points (74%)
   • Bug: 18 points (15%)
   • Task: 13 points (11%)

⏰ BY TIME LOGGED:
   • Story: 156.5h (69%)
   • Bug: 52.0h (23%)
   • Task: 18.5h (8%)

🎯 ESTIMATION ACCURACY:
   • Story: 95% accuracy (Excellent)
   • Bug: 67% accuracy (Needs improvement)
   • Task: 89% accuracy (Good)
```

#### What This Tells You

**Work Distribution:**
- **65% Stories** - Good focus on new features/value
- **22% Bugs** - Significant maintenance work, consider prevention
- **13% Tasks** - Reasonable operational overhead

**Estimation Issues:**
- **Stories well-estimated** - Team understands feature work well
- **Bugs poorly estimated** - Hard to predict fix time (normal!)
- **Tasks well-estimated** - Good understanding of operational work

#### Optimization Strategies

**High Bug Percentage (>30%):**
- Review quality processes: Testing, code review, definition of done
- Consider technical debt cleanup sprints
- Investment in automated testing
- Root cause analysis of recurring issues


### 👥 Developer Performance

⚠️ **Important**: This tool is for **supporting and developing** team members, not for punitive measures or ranking. Use insights to identify coaching opportunities and provide appropriate support.

#### What It Does
Provides individual performance insights while maintaining team context:
- Individual completion rates and velocity trends
- Estimation accuracy by developer
- Focus rate and productivity patterns
- Skill area analysis by work category

#### Sample Individual Report

```
👤 DEVELOPER PERFORMANCE: Alice Johnson
==================================================

📊 SPRINT METRICS:
   • Issues Completed: 8/9 (89%)
   • original estimate (h)s: 21 (Team avg: 18)
   • Focus Rate: 85% (Team avg: 73%)
   • Estimation Accuracy: 92%

📈 CATEGORY PERFORMANCE:
   • Backend Development: 15 pts (Strong)
   • Frontend Development: 6 pts (Learning)
   • Bug Fixes: 0 pts (No exposure)

🎯 OBSERVATIONS:
   • Consistently high completion rate (3 sprints)
   • Above-average focus rate indicates good concentration
   • Strong in backend, developing frontend skills
   • Could benefit from bug triage exposure
```

#### Using Performance Data Constructively

**High Performers:**
- 🏆 **Recognition** - Acknowledge contributions publicly
- 📚 **Growth** - Challenging assignments, learning opportunities
- 🤝 **Mentoring** - Pair with developing team members
- 🔄 **Cross-training** - Expand skills to other areas

**Developing Performers:**
- 🤝 **Support** - Additional pairing, mentoring, resources
- 📚 **Training** - Specific skills development, courses
- 🎯 **Focus** - Smaller, well-defined tasks to build confidence
- ⏰ **Time** - Allow adequate time for learning curve

**Performance Variations:**
- 📊 **Normal** - 20-30% variation between team members is typical
- 🔍 **Investigate** - Sudden changes or sustained low performance
- 🤝 **Support** - Personal issues, skill gaps, process problems
- 📈 **Improvement** - Track trends over time, not single sprints

---

## Interpreting Results

### Reading the Numbers

#### Completion Rates
- **90%+** - Excellent execution, possibly under-committing
- **80-89%** - Good execution, healthy stretch goals
- **70-79%** - Moderate execution, room for improvement
- **60-69%** - Poor execution, investigate causes
- **<60%** - Significant issues, immediate attention needed

#### Focus Rates
- **90%+** - Exceptional focus, minimal interruptions
- **80-89%** - Good focus, normal business interruptions
- **70-79%** - Moderate focus, some multitasking
- **60-69%** - Low focus, significant context switching
- **<60%** - Very fragmented work, process issues

#### Velocity Trends
- **Consistent** - Predictable team, good for planning
- **Increasing** - Team maturing, process improving, or scope creeping
- **Decreasing** - Technical debt, team changes, or complexity increasing
- **Volatile** - Unpredictable factors, need investigation

### Common Patterns and Their Meanings

#### The "Last-Minute Rush"
**Pattern**: Most issues completed in final days of sprint
**Meaning**: Poor work distribution, potential quality issues
**Actions**: Better task breakdown, daily stand-up focus, capacity planning

#### The "Overachiever Anomaly"
**Pattern**: One team member completing significantly more work
**Meaning**: Skill imbalance, work distribution issues, or measurement problems
**Actions**: Investigate workload distribution, skill sharing, pair programming

#### The "Bug Avalanche"
**Pattern**: High percentage of bug work, poor bug estimation
**Meaning**: Quality issues, technical debt, or insufficient testing
**Actions**: Quality process review, automated testing, technical debt sprints

#### The "Planning Paradox"
**Pattern**: Consistent over-commitment but stable velocity
**Meaning**: Team velocity stable but planning optimistic
**Actions**: Adjust planning approach, account for overhead, realistic capacity

---

## Best Practices for Scrum Masters

### 1. Sprint Retrospectives with Data

#### Before the Retrospective
1. **Run Sprint Completion Analysis** - Get concrete completion data
2. **Check Anomaly Detector** - Identify discussion points
3. **Review Worklog Summary** - Understand team focus patterns
4. **Prepare insights, not accusations** - Frame data as team learning

#### During the Retrospective
**Data-Driven Questions:**
- "We completed 78% of our sprint commitment. What helped us succeed with that portion?"
- "Three issues were completed after the sprint. What can we learn from that pattern?"
- "Our focus rate was 73% this sprint. What interrupted our flow?"
- "Backend tasks had lower completion rate. What support might help?"

**Avoid These Pitfalls:**
- ❌ "John only completed 12 points while Mary completed 20"
- ❌ "We failed because we only hit 75% completion"
- ❌ "The data shows you're not working hard enough"
- ✅ "What patterns do we see that we can build on?"

#### After the Retrospective
1. **Track action items** - Use next sprint's data to measure improvement
2. **Share insights** - Communicate learnings with stakeholders
3. **Adjust process** - Apply lessons to planning and daily work

### 2. Sprint Planning with Historical Data

#### Use Planning Tool Results
```
📊 Historical Planning Accuracy:
Last 6 sprints average: 78% completion
Velocity trend: Stable (38-42 points)
Best performance categories: Frontend (85%), DevOps (92%)
Challenge areas: Backend (68%), Bug fixes (45%)
```

#### Planning Adjustments
- **Account for categories** - Plan more conservatively for historically challenging work
- **Use realistic velocity** - Base on actual completion rates, not ideal capacity
- **Buffer for unknowns** - Reserve 10-20% capacity for unplanned work
- **Balance work types** - Avoid sprints with all challenging work

#### Capacity Planning
1. **Check developer performance trends** - Who's available and at what capacity?
2. **Review focus rate patterns** - Account for interruptions and meetings
3. **Consider work type mix** - Balance feature work, bugs, and technical tasks

### 3. Team Development and Support

#### Using Performance Data Constructively

**Individual Development:**
```
Based on last 3 sprints:
• Strong areas: Backend development, estimation accuracy
• Growth areas: Frontend skills, cross-team collaboration
• Support needed: Pairing on frontend tasks, exposure to user testing
```

**Team Health Monitoring:**
- **Focus rate trends** - Are interruptions increasing?
- **Completion rate patterns** - Is team burning out or growing?
- **Work distribution** - Is workload balanced and fair?
- **Skill development** - Are team members growing their capabilities?

#### Coaching Conversations
**Frame data positively:**
- ✅ "The data shows you're strong in backend work. Would you like to explore frontend pairing?"
- ✅ "Your focus rate is excellent. Could you share tips with the team?"
- ✅ "I notice some challenges with estimation in this area. What support would help?"

### 4. Stakeholder Communication

#### Executive Summary Template
```
📊 SPRINT 23 EXECUTIVE SUMMARY

🎯 Delivery: 18/23 planned items completed (78%)
⏰ Effort: 284 hours logged by 6 developers
🏆 Highlights: Frontend features delivered ahead of schedule
⚠️  Challenges: 3 backend items required additional sprint time
📈 Trend: Planning accuracy improving (+5% over 6 sprints)

Next Sprint Focus: Backend capacity support, continued frontend momentum
```

#### Stakeholder Questions You Can Answer
- **"Are we delivering what we commit to?"** → Sprint completion analysis
- **"Is the team productive?"** → Focus rate and velocity data
- **"Where should we invest in training?"** → Performance and category analysis
- **"Are we improving over time?"** → Multi-sprint trending data

### 5. Process Optimization

#### Monthly Process Health Check
1. **Run all analysis tools** on last 4 sprints
2. **Look for patterns** across multiple data points
3. **Identify 1-2 improvement opportunities** (not 10!)
4. **Implement changes gradually** and measure impact

#### Continuous Improvement Cycle
```
1. MEASURE → Run SMT analysis tools
2. ANALYZE → Identify patterns and opportunities
3. EXPERIMENT → Try 1-2 small changes
4. EVALUATE → Use SMT to measure impact
5. STANDARDIZE → Keep what works, discard what doesn't
6. REPEAT → Monthly cycle
```

---

## Use Cases & Scenarios

### Scenario 1: New Scrum Master Taking Over a Team

**Situation**: You've just become Scrum Master for an existing team. You need to understand current performance and identify improvement opportunities.

**SMT Approach**:
1. **Week 1**: Run **Connection Test** and **Projects Lister** to get oriented
2. **Week 2**: **Sprint Completion** analysis on last 3 completed sprints
3. **Week 3**: **Planning Tool** analysis to understand historical trends
4. **Week 4**: **Developer Performance** review (privately) to understand team dynamics

**Insights You'll Gain**:
- Team delivery consistency and areas of strength/challenge
- Planning accuracy and velocity trends
- Individual team member contributions and growth areas
- Process bottlenecks and optimization opportunities

### Scenario 2: Sprint Retrospective Preparation

**Situation**: You want to run a data-driven retrospective focused on concrete improvements rather than vague feelings.

**SMT Approach**:
1. **24 hours before retro**: Run **Sprint Completion** and **Worklog Summary**
2. **2 hours before retro**: Run **Anomaly Detector** to identify discussion points
3. **During retro**: Present data as conversation starters, not judgments
4. **After retro**: Use **Planning Tool** to set realistic goals for improvement

**Sample Retrospective Agenda**:
```
📊 Data Review (10 min): Sprint completion, focus rate, anomalies
🔍 Discussion (30 min): What do these patterns tell us?
💡 Insights (10 min): What's working well? What's challenging?
🎯 Actions (10 min): 1-2 specific experiments to try
```

### Scenario 3: Planning Accuracy Problems

**Situation**: Your team consistently over-commits and under-delivers. Stakeholders are frustrated with missed commitments.

**SMT Approach**:
1. **Planning Tool** analysis across 6+ sprints to identify trends
2. **Issue Type Summary** to see if certain work types are problematic
3. **Sprint Completion** analysis to understand where work spills over
4. **Developer Performance** review to check capacity assumptions

**Common Findings & Solutions**:
- **Over-estimation of capacity** → Use historical completion rates for planning
- **Underestimation of specific work types** → Category-based planning buffers
- **Interruptions not accounted for** → Reserve capacity for unplanned work
- **Scope creep during sprint** → Better sprint commitment discipline

### Scenario 4: Team Performance Concerns

**Situation**: Management has concerns about team productivity. You need objective data to assess the situation.

**SMT Approach**:
1. **Worklog Summary** to understand actual time investment patterns
2. **Developer Performance** to identify if issues are individual or systemic
3. **Anomaly Detector** to find specific issues requiring attention
4. **Issue Type Summary** to see if work mix is affecting productivity

**Possible Outcomes**:
- **Team is actually performing well** → Data validates team, addresses management concerns
- **Systemic process issues found** → Focus on process improvement, not people
- **Specific support needs identified** → Targeted training or resource allocation
- **External factors affecting performance** → Data supports need for organizational changes

### Scenario 5: Scaling Team Success

**Situation**: Your team has been performing well, and you want to understand what's working so you can help other teams or maintain performance as you grow.

**SMT Approach**:
1. **All analysis tools** across 6+ sprints to build comprehensive performance picture
2. **Planning Tool** to document planning practices and accuracy
3. **Developer Performance** to understand skill distribution and growth patterns
4. **Focus rate analysis** to understand environmental factors supporting success

**Documentation for Scaling**:
- Process patterns that correlate with high performance
- Team skill mix and development approaches
- Environmental factors (focus time, interruption management)
- Planning practices and capacity management techniques

### Scenario 6: Post-Incident Analysis

**Situation**: A major bug reached production, causing customer impact. You need to understand what went wrong in your development process.

**SMT Approach**:
1. **Sprint Completion** analysis for sprints containing the problematic work
2. **Issue Type Summary** to understand bug/quality work balance
3. **Anomaly Detector** to see if there were warning signs
4. **Worklog Summary** to understand if time pressure was a factor

**Analysis Questions**:
- Did sprint pressure contribute to quality shortcuts?
- Was there adequate time allocated for testing and review?
- Are bug patterns visible in historical data?
- Did workload distribution affect quality focus?

---

This user guide provides the foundation for effective use of ScrumMaster Tools in real-world agile environments. Remember that data is a tool for improvement, not judgment—use these insights to support your team's growth and success.

## Related Documentation

- **[Configuration Guide](CONFIGURATION.md)** - Detailed setup and configuration instructions
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Solutions for technical issues and common problems
- **[Tools Reference](TOOLS.md)** - Comprehensive documentation for each analysis tool
- **[API Documentation](API.md)** - Technical details for Jira integration and extensions
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute and develop new features
- **[Architecture Guide](ARCHITECTURE.md)** - Technical architecture and system design