Potential pitfalls and failure modes

- Concurrency / Race conditions: localStorage writes are synchronous in the browser; however, if multiple tabs write at the same time, last write wins. There is no transactional append, so test harnesses emulate single-tab behavior.
- Malformed or injected entries: If localStorage contains objects or non-string types, the implementation filters to keep strings only; consider boundary testing for very long strings and control characters.
- Storage quota: LocalStorage quotas vary; writing many large strings may fail. The implementation limits to 5 items and uses truncation in UI only.
- Accessibility: The implementation adds ARIA roles (listbox/option) and attributes. In real deployment ensure screen reader and focus management is fully tested in user environment.
- Privacy: Opt-out prevents persistence to localStorage but keeps in-session history. Clearing history removes both storage and session data.
- Cross-origin and storage scope: localStorage is origin-scoped, so multiple subdomains have separate histories.
