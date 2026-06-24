# Universal Dragon Polyglot Architecture

Universal Dragon uses `.ud` as the top-level language.

Python, C, C++, Java, Kotlin, HTML, TypeScript, and other languages are not the main identity. They are internal adapters controlled by UD.

## Rule

User writes:

```ud
brain universal_dragon
say "hello"
use python as tool
use html as page
use typescript as app
use c as core
