
# Flowchart 1: `detect_language()`

```text
                              START
                                │
                                ▼
                 ┌───────────────────────────┐
                 │ Receive Input Text        │
                 └─────────────┬─────────────┘
                               │
                               ▼
                 ┌───────────────────────────┐
                 │ Detect Language           │
                 │ detect(text)              │
                 └─────────────┬─────────────┘
                               │
                     ┌─────────▼─────────┐
                     │ Detection Success? │
                     └───────┬─────┬─────┘
                             │Yes  │No
                             │     │
                             ▼     ▼
              ┌──────────────────┐ ┌──────────────────┐
              │ Return Language  │ │ Return "en"      │
              │ Code (e.g., ur)  │ │ (Default)        │
              └──────────┬───────┘ └──────────┬───────┘
                         │                    │
                         └──────────┬─────────┘
                                    ▼
                                   END
```

---

# Flowchart 2: `to_english()`

```text
                               START
                                 │
                                 ▼
                ┌────────────────────────────────┐
                │ Receive Text & Source Language │
                └───────────────┬────────────────┘
                                │
                                ▼
                  ┌────────────────────────────┐
                  │ Source Language = English? │
                  └──────────────┬─────────────┘
                                 │
                    Yes          │          No
                     │           │
                     ▼           ▼
          ┌────────────────┐   ┌────────────────────────────┐
          │ Return Original │   │ Translate using           │
          │ Text            │   │ Google Translator         │
          └────────┬────────┘   └──────────────┬────────────┘
                   │                           │
                   │                 ┌─────────▼──────────┐
                   │                 │ Translation Success?│
                   │                 └─────────┬─────┬────┘
                   │                           │Yes  │No
                   │                           │     │
                   │                           ▼     ▼
                   │          ┌────────────────────┐ ┌─────────────────────┐
                   │          │ Return English     │ │ Log Exception       │
                   │          │ Translation        │ │ Return Original Text│
                   │          └─────────┬──────────┘ └─────────┬───────────┘
                   │                    │                      │
                   └────────────────────┴──────────────────────┘
                                        │
                                        ▼
                                       END
```

---

# Flowchart 3: `from_english()`

```text
                               START
                                 │
                                 ▼
                ┌────────────────────────────────┐
                │ Receive English Text & Target  │
                │ Language                       │
                └───────────────┬────────────────┘
                                │
                                ▼
                  ┌────────────────────────────┐
                  │ Target Language = English? │
                  └──────────────┬─────────────┘
                                 │
                    Yes          │          No
                     │           │
                     ▼           ▼
          ┌────────────────┐   ┌────────────────────────────┐
          │ Return Original │   │ Translate from English    │
          │ English Text    │   │ using Google Translator   │
          └────────┬────────┘   └──────────────┬────────────┘
                   │                           │
                   │                 ┌─────────▼──────────┐
                   │                 │ Translation Success?│
                   │                 └─────────┬─────┬────┘
                   │                           │Yes  │No
                   │                           │     │
                   │                           ▼     ▼
                   │          ┌────────────────────┐ ┌─────────────────────┐
                   │          │ Return Translated  │ │ Log Exception       │
                   │          │ Text               │ │ Return English Text │
                   │          └─────────┬──────────┘ └─────────┬───────────┘
                   │                    │                      │
                   └────────────────────┴──────────────────────┘
                                        │
                                        ▼
                                       END
```

