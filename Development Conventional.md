# Conventional Commits 1.0.0

## Summary
The Conventional Commits specification is a lightweight convention on top of commit messages. It provides an easy set of rules for creating an explicit commit history; which makes it easier to write automated tools on top of. This convention dovetails with [SemVer](https://semver.org), by describing the features, fixes, and breaking changes made in commit messages.

The commit message should be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

The commit contains the following structural elements, to communicate intent to the consumers of your library:

|Type|Explaination|
|------------- |-------------|
|Add |a commit that `introduces` a new feature to the codebase|
|Update |a commit that `update` performance or minor change in codebase|
|Fix |a commit that `patches` a bug in codebase|
|Style |a commit that `formatting`, missing semi colons, etc; no production code change|
|Refactor |a commit that `refactoring` codebase, eg. renaming a variable|
|Docs |a commit that `changes to the documentation`|
|Test |a commit that `adding missing tests`, `refactoring tests` **no production code change**|
|Debug |a commit that use when you `debug`in codebase|
|BREAKING CHANGE| a commit that has a footer `BREAKING CHANGE`, or appends a `!` after the **type/scope**, introduces a breaking API change (correlating with **MAJOR** in Semantic Versioning). **A BREAKING CHANGE can be part of commits of any type.**|
