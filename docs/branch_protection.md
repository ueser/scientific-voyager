# Branch Protection and Code Review Guidelines

This document outlines the branch protection rules and code review guidelines for the Scientific Voyager project.

## Branch Protection Rules

The following branch protection rules should be configured in the GitHub repository settings:

### For `main` branch:

- **Require pull request reviews before merging**
  - Required approving reviews: 1
  - Dismiss stale pull request approvals when new commits are pushed
  - Require review from Code Owners

- **Require status checks to pass before merging**
  - Require branches to be up to date before merging
  - Required status checks:
    - Python Tests (all matrix configurations)
    - Lint checks

- **Require signed commits**

- **Include administrators**

- **Restrict who can push to matching branches**
  - Restrict to repository administrators and designated maintainers

### For `develop` branch:

- **Require pull request reviews before merging**
  - Required approving reviews: 1
  - Dismiss stale pull request approvals when new commits are pushed

- **Require status checks to pass before merging**
  - Require branches to be up to date before merging
  - Required status checks:
    - Python Tests (all matrix configurations)
    - Lint checks

- **Include administrators**

## Code Review Guidelines

### For Reviewers

1. **Response Time**: Aim to respond to review requests within 24 hours (business days)

2. **Review Scope**:
   - Code correctness: Does the code do what it's supposed to do?
   - Code quality: Is the code well-structured, readable, and maintainable?
   - Test coverage: Are there appropriate tests for the changes?
   - Documentation: Are the changes properly documented?
   - Security: Are there any security concerns?
   - Performance: Are there any performance concerns?

3. **Review Approach**:
   - Be constructive and respectful
   - Provide specific, actionable feedback
   - Distinguish between required changes and suggestions
   - Explain the reasoning behind your feedback
   - Provide examples or references when helpful

4. **Review Checklist**:
   - Does the code follow the project's style guidelines?
   - Are variable/function names clear and descriptive?
   - Is the code DRY (Don't Repeat Yourself)?
   - Are edge cases handled appropriately?
   - Is error handling implemented correctly?
   - Is the code efficient?
   - Are there any potential security vulnerabilities?
   - Is the documentation complete and accurate?

### For Authors

1. **PR Preparation**:
   - Keep PRs focused and reasonably sized
   - Provide a clear description of the changes
   - Link to relevant issues
   - Include any necessary context or background information
   - Run tests locally before submitting
   - Ensure all CI checks pass

2. **Responding to Feedback**:
   - Respond to all comments
   - Be open to feedback and suggestions
   - Explain your reasoning when disagreeing with feedback
   - Make requested changes promptly
   - Request clarification if feedback is unclear

3. **PR Checklist**:
   - Does the PR address the issue it claims to address?
   - Have you added/updated tests for your changes?
   - Have you updated documentation as needed?
   - Have you checked for any unintended side effects?
   - Have you run the tests locally?
   - Have you addressed all review comments?

## Code Review Process

1. **Author creates a PR**:
   - Fill out the PR template
   - Assign reviewers
   - Link to relevant issues

2. **Reviewers review the PR**:
   - Comment on specific lines of code
   - Approve, request changes, or comment

3. **Author addresses feedback**:
   - Make requested changes
   - Respond to comments
   - Request re-review if needed

4. **Reviewers re-review**:
   - Verify changes address feedback
   - Approve if satisfied

5. **PR is merged**:
   - Author or reviewer merges the PR
   - Delete the branch if no longer needed

## Merge Criteria

A PR can be merged when:

1. It has been approved by at least one reviewer
2. All CI checks pass
3. All requested changes have been addressed
4. The branch is up to date with the target branch

## Handling Disagreements

If there is a disagreement between the author and reviewer:

1. Discuss the issue in the PR comments
2. Provide reasoning and evidence for your position
3. Consider alternatives that address both concerns
4. If needed, involve a third team member for mediation
5. Document the decision and reasoning
