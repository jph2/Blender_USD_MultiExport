# GitHub Issues & Ticketing System

This repository uses **GitHub's built-in Issues system** for bug tracking, feature requests, and project management.

## 🎯 What's Set Up

### Issue Templates

Three issue templates are configured in `.github/ISSUE_TEMPLATE/`:

1. **🐛 Bug Report** (`bug_report.yml`)
   - Structured form for reporting bugs
   - Captures: description, steps to reproduce, expected/actual behavior, Blender version, OS, screenshots
   - Automatically labels issues as `bug` and `needs-triage`

2. **💡 Feature Request** (`feature_request.yml`)
   - Structured form for suggesting features
   - Captures: problem statement, proposed solution, use case, priority, mockups
   - Automatically labels issues as `enhancement` and `needs-triage`

3. **❓ Question** (`question.yml`)
   - Form for asking questions
   - Captures: question, context, what you've tried, Blender version
   - Automatically labels issues as `question` and `needs-triage`

### Issue Template Configuration

The `config.yml` file:
- Disables blank issues (users must use a template)
- Provides helpful links to Discussions and Documentation
- Guides users to search existing issues first

## 🚀 How It Works

### For Users

1. **Go to Issues**: https://github.com/jph2/Blender_USD_StableExport/issues
2. **Click "New Issue"**
3. **Select a template** (Bug Report, Feature Request, or Question)
4. **Fill out the form** - all required fields are marked
5. **Submit** - the issue is automatically created with appropriate labels

### For Maintainers

- Issues are automatically labeled based on template type
- Use labels to filter and organize issues
- Use milestones to track progress
- Use projects for kanban-style management

## 📋 Recommended Labels

Create these labels in GitHub (Settings > Labels):

### Type Labels
- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `question` - Question about usage
- `documentation` - Documentation improvements

### Status Labels
- `needs-triage` - Needs review/prioritization
- `help-wanted` - Good for contributors
- `good-first-issue` - Good for new contributors
- `in-progress` - Currently being worked on
- `blocked` - Blocked by something else

### Priority Labels
- `priority: critical` - Critical priority
- `priority: high` - High priority
- `priority: medium` - Medium priority
- `priority: low` - Low priority

### Category Labels
- `ui` - User interface related
- `export` - Export functionality
- `endpoint` - Endpoint management
- `performance` - Performance related
- `compatibility` - Compatibility issues

## 🔧 Additional GitHub Features

### Projects (Kanban Boards)

Create a GitHub Project for visual project management:
1. Go to Projects tab
2. Click "New Project"
3. Choose "Board" template
4. Add columns: Backlog, In Progress, Review, Done
5. Link issues to the project

### Milestones

Create milestones to track progress:
1. Go to Issues > Milestones
2. Create milestones like "v1.0.0", "v1.1.0", etc.
3. Assign issues to milestones
4. Track progress automatically

### Discussions

Enable GitHub Discussions for:
- General questions
- Community discussions
- Usage tips and tricks
- Non-issue conversations

## 📊 Usage Tips

### For Bug Reports

- **Be specific**: Include exact steps to reproduce
- **Include versions**: Blender version, addon version, OS
- **Add screenshots**: Visual evidence helps a lot
- **Check duplicates**: Search existing issues first

### For Feature Requests

- **Describe the problem**: Why is this feature needed?
- **Propose a solution**: How should it work?
- **Provide use cases**: Real-world scenarios help
- **Set priority**: Help us prioritize

### For Questions

- **Check documentation first**: README, Research doc, etc.
- **Search existing issues**: Your question might already be answered
- **Provide context**: What are you trying to accomplish?

## 🔗 Quick Links

- **Create Bug Report**: https://github.com/jph2/Blender_USD_StableExport/issues/new?template=bug_report.yml
- **Request Feature**: https://github.com/jph2/Blender_USD_StableExport/issues/new?template=feature_request.yml
- **Ask Question**: https://github.com/jph2/Blender_USD_StableExport/issues/new?template=question.yml
- **View All Issues**: https://github.com/jph2/Blender_USD_StableExport/issues
- **Contributing Guide**: [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**Note**: Issue templates are automatically available once pushed to GitHub. No additional setup required!

